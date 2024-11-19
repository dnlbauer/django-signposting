[![Python package](https://github.com/dnlbauer/django-signposting/actions/workflows/python-package.yml/badge.svg)](https://github.com/dnlbauer/django-signposting/actions/workflows/python-package.yml)

# FAIR signposting middleware for Django

`django_signposting` is a Django middleware library that facilitates the addition of
FAIR signposting headers to HTTP responses.
This middleware helps in making your data more FAIR (Findable, accessible, interoperable, reuseable) by
embedding signposting headers in responses, guiding clients to relevant resources linked to the response content.

Based on the [Signposting](https://github.com/stain/signposting) library.

## Features
- Automatically adds signposting headers to HTTP responses.
- Signposts can be added manually or automatically be parsed from JSON-LD/schema.org
- Supports multiple relation types with optional media type specification.
- Easily integrable with existing Django applications.

## Installation

```bash
pip install django-signposting
```

## Usage

### Automatic parsing of JSON-LD

To enable automatic parsing of JSON-LD, add the following middleware classes to your Django project's MIDDLEWARE setting in settings.py:

```python
MIDDLEWARE = [
    ...,
    'django_signposting.middleware.SignpostingMiddleware',
    'django_signposting.middleware.JsonLdSignpostingParserMiddleware',
    ...,
]
```

This setup allows django_signposting to extract JSON-LD embedded in HTML `<script type="application/ld+json">` tags
and add the corresponding signposting headers.
It’s compatible with tools that provide JSON-LD, such as [django-json-ld](https://pypi.org/project/django-json-ld/).

> Note: The middleware order is important! Place `SignpostingMiddleware` before `JsonLdSignpostingParserMiddleware` to ensure proper extraction and processing of JSON-LD content.

### Manual signposting

For cases where JSON-LD is not embedded, or you want to specify headers manually, you can use the `add_signposts` utility.

1. **Add Middleware**: Add the `SignpostingMiddleware` to your Django project's `MIDDLEWARE` setting in `settings.py`:

```python
MIDDLEWARE = [
    ...,
    'django_signposting.middleware.SignpostingMiddleware',
    ...,
]
```

2. **Add Signposts to your Views:** Use the `add_signposts` utility function:

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

## Signposts are formatted and added as Link headers by the middleware

```bash
curl -I http://localhost:8000
HTTP/2 200 
...
link: <https://schema.org/Dataset> ; rel="type" ,
      <https://orcid.org/0000-0001-9447-460X> ; rel="author" ,
      <https://example.com/download.zip> ; rel="item" ; type="application/zip"
```

## TODO

- [ ] Option to add signposts in HTML via <link> elements.


## License

Licensed under the MIT License.
