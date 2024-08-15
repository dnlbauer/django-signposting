from django.http import HttpResponse


def add_signposts(response: HttpResponse, **kwargs):
    """ Adds signposting headers to the responses.
    params:
      response - the response object
      kwargs - a map of relation types to a list of corresponding links. Each link can be a link or a tuple of link and media type.
    """

    if not hasattr(response, '_signposts'):
        response._signposts = {}

    for key in kwargs.keys():

        values = kwargs[key]
        if isinstance(values, str) or isinstance(values, tuple):
            values = [values]

        if key not in response._signposts:
            response._signposts[key] = values
        else:
            response._signposts[key] += values