from typing import Callable
from django.http import HttpRequest, HttpResponse


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

    def _add_signposts(self, response: HttpResponse, typed_links: dict[str, list[str|tuple[str, str]]]):
        """ Adds signposting headers to the respones.
        params:
          response - the response object
          typed_links - a map of relation types to a list of corresponding links. Each link can be a link or a tuple of link and media type.
        """
        link_snippets = []
        for relation_type in typed_links.keys():
            links = typed_links.get(relation_type, [])
            for link in links:
                if isinstance(link, tuple) and len(link) > 1:
                    link_snippets.append(f'<{link[0]}> ; rel="{relation_type}" ; type="{link[1]}"')
                else:
                    link_snippets.append(f'<{link}> ; rel="{relation_type}"')

        response["Link"] = " , ".join(link_snippets)

