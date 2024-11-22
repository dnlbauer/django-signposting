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

### Signposts are formatted and added as Link headers

```bash
curl -I http://localhost:8000
HTTP/2 200 
...
link: <https://schema.org/Dataset> ; rel="type" ,
      <https://orcid.org/0000-0001-9447-460X> ; rel="author" ,
      <https://example.com/download.zip> ; rel="item" ; type="application/zip"
```

## Installation

```bash
pip install django-signposting
```

## Usage

### Automatic parsing of JSON-LD

The library can automatically add signposts to web pages that already make
metadata available via JSON-LD in HTML via `<script type="application/ld+json">` tags, i.e.:

```HTML
<!DOCTYPE html>
<html>
<head>

<script type="application/ld+json">{"@context": "https://schema.org", "@type": ["WebSite", "Dataset"], "author": {"@type": "Person", "name": "Daniel Bauer", "url": "https://orcid.org/0000-0001-9447-460X"}, "description": "A dataset of things.", "hasPart": [{"@type": "ImageObject", "encodingFormat": "image/png", "url": "http://example.com/image.png"}, {"@type": "ImageObject", "encodingFormat": "image/png", "url": "http://example.com/image2.png"}], "license": {"@type": "CreativeWork", "name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/"}, "name": "My Dataset", "sameAs": [{"@type": "MediaObject", "contentUrl": "https://example.com/download.zip", "encodingFormat": "application/zip"}, {"@type": "MediaObject", "contentUrl": "https://example.com/metadata.json"}], "url": "https://example.com"}</script>
</head>
<body>
    <p>Hello, world!</p>
</body>
</html>
```

To enable automatic parsing of JSON-LD, add the following middleware classes to your Django project's MIDDLEWARE setting in settings.py:

```python
MIDDLEWARE = [
    ...,
    'django_signposting.middleware.SignpostingMiddleware',
    'django_signposting.middleware.JsonLdSignpostingParserMiddleware',
    ...,
]
```

This extracts supported metadatad properties from JSON-LD and adds the corresponding signposting headers to the `HttpResponse` automatically.

Automatic parsing is compatible with extensions that provide JSON-LD as part of a web page, such as [django-json-ld](https://pypi.org/project/django-json-ld/).
It can also extract signposts from rich metadata descriptions of datasets such as detached [RO-Crates](https://www.researchobject.org/ro-crate) (see [example views](./example/example/views.py)).

> Note: The middleware order is important! Place `SignpostingMiddleware` before `JsonLdSignpostingParserMiddleware` to ensure proper extraction and processing of JSON-LD content.

## Alternative approaches

### Manual signposting

For cases where there is no embedded JSON-LD, or you want to specify additional headers manually, you can use the `add_signposts` utility function.
This still requires the `SignpostingMiddleware` to inject the links into
the response:

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

### Manual parsing of JSON-LD

If you have metadata in JSON-LD available, but it is not rendered as part of the response, you can still parse it and add the signposting links manually:

```python
from django.http import HttpResponse
from django_signposting.utils import add_signposts, jsonld_to_signposts

response = HttpResponse("Hello World")
json_ld = {
    "@context": "http://schema.org/",
    "@graph": [
        ...
    ]
}
signposts = jsonld_to_signposts(json_ld)
add_signposts(response, **signposts)
```

### Add signposts as HTML links instead of headers

In cases where you want to include signposting directly in the HTML response rather than as HTTP headers
(for example because headers are overwritten by a proxy or something else),
you can use the `HtmlSignpostingMiddleware` instead of `SignpostingMiddleware`.

This middleware automatically adds <link> elements to the HTML <head> section based
on the detected signposting metadata and produces output similar to the one shown here:

```HTML
<!DOCTYPE html>
<html>
 <head>
  (...)
  <link href="http://schema.org/WebSite" rel="type"/>
  <link href="http://schema.org/Dataset" rel="type"/>
  <link href="https://orcid.org/0000-0001-9447-460X" rel="author"/>
  <link href="https://creativecommons.org/licenses/by/4.0/" rel="license"/>
  <link href="https://example.com" rel="cite-as"/>
  <link href="https://example.com/download.zip" rel="describedby" type="application/zip"/>
  <link href="https://example.com/metadata.json" rel="describedby"/>
  <link href="http://example.com/image.png" rel="item" type="image/png"/>
  <link href="http://example.com/image2.png" rel="item" type="image/png"/>
 </head>
 ...
</html>
```

## TODO

- [ ] Option to add signposts in HTML via <link> elements.
- [ ] Add support for link sets
- [ ] Add support for specifying profile extension attribute

## License

Licensed under the MIT License.
