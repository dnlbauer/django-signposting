from typing import Callable
from django.http import HttpRequest, HttpResponse
from signposting import Signpost


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
        """ Adds signposting headers to the respones.
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

