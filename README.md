# FAIR signposting for Django

`django_signposting` is a Django middleware library that facilitates the addition of
FAIR signposting headers to HTTP responses.
This middleware helps in making your data more FAIR (Findable, accessible, interoperable, reuseable) by
embedding signposting headers in responses, guiding clients to relevant resources linked to the response content.

## Features
- Automatically adds signposting headers to HTTP responses.
- Supports multiple relation types with optional media type specification.
- Easily integrable with existing Django applications.

## Installation

```bash
pip install django_signposting
```

## Usage

### 1. Add Middleware

Add the middleware to your Django project's `MIDDLEWARE` setting in `settings.py`:

```python
MIDDLEWARE = [
    ...,
    'django_signposting.middleware.SignpostingMiddleware',
    ...,
]
```

### 2. Add Signposts to your Views

You can add signposting headers in your Django views using the provided `add_signposts` utility function.
Here's how you can use it:

```python
from django.http import HttpResponse
from django_signposting.util import add_signposts

def my_view(request):
    response = HttpResponse("Hello, world!")
    
    # Add signpostings as string
    add_signposts(response,
                  type="https://schema.org/Dataset",
                  author="https://orcid.org/0000-0001-9447-460X")

    return response
```

Multiple links with the same link type can be added as lists and the content type of a link
can be defined by using tuples:

```python

from django.http import HttpResponse
from django_signposting.util import add_signposts

def my_view(request):
    response = HttpResponse("Hello, world!")

    # Add signpostings as string
    add_signposts(response,
                  type="https://schema.org/Dataset",
                  author="https://orcid.org/0000-0001-9447-460X",
                  item=[
                      ("https://example.com/image.png", "image/png"),
                      ("https://example.com/download.zip", "application/zip")
                  ])

    return response
```

### 3. Signposts are formatted and added as Link headers by the middleware:

```bash
curl -I https://example.com
HTTP/2 200 
...
link: <https://schema.org/Dataset> ; rel="type" ,
      <https://orcid.org/0000-0001-9447-460X> ; rel="author" ,
      <https://example.com/image.png> ; rel="item" ; type="application/json+ld"
```

## License

Licensed under the MIT License.