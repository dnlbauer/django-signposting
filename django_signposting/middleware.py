from typing import Callable
from django.http import HttpRequest, HttpResponse
from signposting import Signpost

from bs4 import BeautifulSoup
import json
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .utils import jsonld_to_signposts


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
                    signposts = jsonld_to_signposts(jsonld)

                    response._signposts = signposts
                except json.JSONDecodeError as e:
                    print(e)
                    continue

        return response
