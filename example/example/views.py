from django.http import HttpResponse
from django_signposting.utils import add_signposts

from signposting import Signpost, LinkRel

def my_view(request):
    response = HttpResponse("Hello, world!")
    
    # Add signpostings as string
    add_signposts(
        response,
        Signpost(LinkRel.type, "http://schema.org/Dataset"),
        Signpost(LinkRel.author, "https://orcid.org/0000-0001-9447-460X")
    )

    return response