[![Python package](https://github.com/dnlbauer/django-signposting/actions/workflows/python-package.yml/badge.svg)](https://github.com/dnlbauer/django-signposting/actions/workflows/python-package.yml)

# FAIR signposting for Django

`django_signposting` is a Django middleware library that facilitates the addition of
FAIR signposting headers to HTTP responses.
This middleware helps in making your data more FAIR (Findable, accessible, interoperable, reuseable) by
embedding signposting headers in responses, guiding clients to relevant resources linked to the response content.

Based on the [Signposting](https://github.com/stain/signposting) library.

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
from django_signposting.utils import add_signposts
from signposting import Signpost, LinkRel

def my_view(request):
    response = HttpResponse("Hello, world!")
    
    # Add signpostings as string
    add_signposts(
        response,
        Signpost(LinkRel.type, "https://schema.org/Dataset"),
        Signpost(LinkRel.author, "https://orcid.org/0000-0001-9447-460X")
        Signpost(LinkRel.item, "https://example.com/download.zip", "application/zip")
    )

    return response
```

### 3. Signposts are formatted and added as Link headers by the middleware:

```bash
curl -I https://example.com
HTTP/2 200 
...
link: <https://schema.org/Dataset> ; rel="type" ,
      <https://orcid.org/0000-0001-9447-460X> ; rel="author" ,
      <https://example.com/download.zip> ; rel="item" ; type="application/zip"
```

## License

Licensed under the MIT License.
