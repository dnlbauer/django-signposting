import json
from django.http import HttpResponse
from rdflib import Graph
from signposting import Signpost, LinkRel
import re

from django_signposting import sparql


def add_signposts(response: HttpResponse, *args: Signpost):
    """ Adds signposting headers to the responses.
    params:
      response - the response object
      args - a list of signposts to add to this resposnse.
    """

    if not hasattr(response, '_signposts'):
        response._signposts = []

    for signpost in args:
        if signpost not in response._signposts:
            response._signposts.append(signpost)


def select_url(elements: tuple[str, ...]) -> str | None:
    def is_url(url: str) -> bool:
        url_pattern = re.compile(
            r"^(https?|ftp)://"  # protocol
            r"(?:(?:[a-zA-Z0-9-_]+\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,6})"  # domain
            r"(?::\d{1,5})?"  # optional port
            r"(?:/.*)?$"  # path
        )
        return bool(url_pattern.match(url))

    for elem in elements[::-1]:
        if is_url(str(elem)):
            return str(elem)
    return None


def jsonld_to_signposts(jsonld: dict) -> []:
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
        author = select_url(author)
        if author:
            signposts.append(Signpost(LinkRel.author, author))

    license = next(iter(sparql.license_query(g, rootElement)), [])
    license = select_url(license)
    if license:
        signposts.append(Signpost(LinkRel.license, license))

    citations = sparql.cite_query(g, rootElement)
    for citation in citations:
        citation = select_url(citation)
        if citation:
            signposts.append(Signpost(LinkRel.cite_as, citation))

    sameas = sparql.sameas_query(g, rootElement)
    for sa in sameas:
        sa_media_type = sa[-1]
        sa = select_url(sa[:-1])
        if sa:
            signposts.append(Signpost(LinkRel.describedby, sa, sa_media_type))

    items = sparql.item_query(g, rootElement)
    for item in items:
        item_media_type = item[-1]
        item = select_url(item[:-1])
        if item:
            signposts.append(Signpost(LinkRel.item, item, item_media_type))
    return signposts
