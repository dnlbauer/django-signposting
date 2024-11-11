from typing import Callable
from django.http import HttpRequest, HttpResponse
from signposting import Signpost, LinkRel

from bs4 import BeautifulSoup
import re
import json
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from rdflib import Graph
from . import sparql


class SignpostingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # no signposts on errors
        if response.status_code >= 400:
            return response

        if not hasattr(response, "_signposts"):
            return response
        self._add_signposts(response, response._signposts)

        return response

    def _add_signposts(self, response: HttpResponse, signposts: list[Signpost]):
        """Adds signposting headers to the respones.
        params:
          response - the response object
          signposts - a list of Signposts
        """

        link_snippets = []
        for signpost in signposts:
            link_snippets.append(f'<{signpost.target}> ; rel="{signpost.rel}"')
            if signpost.type:
                link_snippets[-1] += f' ; type="{signpost.type}"'

        response["Link"] = " , ".join(link_snippets)


class JsonLdSignpostingParserMiddleware(MiddlewareMixin):
    def is_url(self, url: str) -> bool:
        url_pattern = re.compile(
            r"^(https?|ftp)://"  # protocol
            r"(?:(?:[a-zA-Z0-9-_]+\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,6})"  # domain
            r"(?::\d{1,5})?"  # optional port
            r"(?:/.*)?$"  # path
        )
        return bool(url_pattern.match(url))

    def select_url(self, elements: tuple[str, ...]) -> str | None:
        for elem in elements[::-1]:
            if self.is_url(str(elem)):
                return str(elem)
        return None

    def _jsonld_to_signposts(self, jsonld: dict) -> dict:
        signposts = []
        # TODO use jsonld context in query as prefix
        g = Graph().parse(data=json.dumps(jsonld), format="json-ld")

        rootElement = next(iter(sparql.root_element_query(g)), None)
        if rootElement:
            rootElement = rootElement[0]
        else:
            print("No root element found")
            return {}

        types = sparql.type_query(g, rootElement)
        for type in types:
            signposts.append(Signpost(LinkRel.type, str(type[0])))

        authors = sparql.author_query(g, rootElement)
        for author in authors:
            author = self.select_url(author)
            if author:
                signposts.append(Signpost(LinkRel.author, author))

        license = next(iter(sparql.license_query(g, rootElement)), [])
        license = self.select_url(license)
        if license:
            signposts.append(Signpost(LinkRel.license, license))

        citations = sparql.cite_query(g, rootElement)
        for citation in citations:
            citation = self.select_url(citation)
            if citation:
                signposts.append(Signpost(LinkRel.cite_as, citation))

        sameas = sparql.sameas_query(g, rootElement)
        for sa in sameas:
            sa_media_type = sa[-1]
            sa = self.select_url(sa[:-1])
            if sa:
                signposts.append(Signpost(LinkRel.describedby, sa, sa_media_type))

        items = sparql.item_query(g, rootElement)
        for item in items:
            item_media_type = item[-1]
            item = self.select_url(item[:-1])
            if item:
                signposts.append(Signpost(LinkRel.item, item, item_media_type))
        return signposts

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        if not getattr(settings, "SIGNPOSTING_PARSE_JSONLD", True):
            return response

        if response.get("Content-Type", "").startswith("text/html"):
            soup = BeautifulSoup(response.content, "html.parser")
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    jsonld = json.loads(script.string)
                    signposts = self._jsonld_to_signposts(jsonld)
                    response._signposts = signposts
                except json.JSONDecodeError as e:
                    print(e)
                    continue

        return response
