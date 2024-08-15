from django.http import HttpResponse
from django_signposting.middleware import SignpostingMiddleware


def test_middleware_no_signposting():
    response = HttpResponse()
    response.status_code = 200

    middleware = SignpostingMiddleware(lambda request: response)
    response = middleware(None)
    assert "Link" not in response.headers


def test_middleware_signposting():
    response = HttpResponse()
    response.status_code = 200
    response._signposts = {"author": ["http://example.com"]}

    middleware = SignpostingMiddleware(lambda request: response)
    response = middleware(None)
    assert response.headers["Link"] == '<http://example.com> ; rel="author"'


def test_middleware_multiple_signposts():
    response = HttpResponse()
    response.status_code = 200
    response._signposts = {
        "author": [
            "http://example.com",
            "http://example2.com"
        ],
        "cite-as": [
            "http://example3.com"
        ]
    }

    middleware = SignpostingMiddleware(lambda request: response)
    response = middleware(None)
    links = [x.strip() for x in response.headers["Link"].split(",")]
    assert '<http://example.com> ; rel="author"' in links
    assert '<http://example2.com> ; rel="author"' in links
    assert '<http://example3.com> ; rel="cite-as"' in links


def test_middleware_signpost_with_content_type():
    response = HttpResponse()
    response.status_code = 200
    response._signposts = {
        "item": [
            ("http://example.com", "test/json"),
        ]
    }

    middleware = SignpostingMiddleware(lambda request: response)
    response = middleware(None)
    assert response.headers["Link"] == '<http://example.com> ; rel="item" ; type="test/json"'


def test_middleware_ignore_error_responses():
    response = HttpResponse()
    response.status_code = 400
    response._signposts = {
        "author": ["https://example.com"]
    }

    middleware = SignpostingMiddleware(lambda request: response)
    response = middleware(None)
    assert "Link" not in response.headers
