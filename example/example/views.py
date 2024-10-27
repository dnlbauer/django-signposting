from django.http import HttpResponse
from django_signposting.utils import add_signposts

def my_view(request):
    response = HttpResponse("Hello, world!")
    
    # Add signpostings as string
    add_signposts(response,
                  type="https://schema.org/Dataset",
                  author="https://orcid.org/0000-0001-9447-460X")

    return response