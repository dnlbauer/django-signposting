from django.http import HttpResponse
from signposting import Signpost


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
