from bs4 import BeautifulSoup
from django.http import HttpResponse
from django_signposting.middleware import HtmlSignpostingMiddleware
from signposting import LinkRel, Signpost


def test_middleware_no_signposting():
    response = HttpResponse("<html><head></head><body></body></html>")
    response.status_code = 200

    middleware = HtmlSignpostingMiddleware(lambda request: response)
    response = middleware(None)
    assert "link" not in response.content.decode("utf-8")


def test_middleware_signposting():
    response = HttpResponse("<html><head></head><body></body></html>")
    response.status_code = 200
    response._signposts = [
        Signpost(LinkRel.author, "http://example.com")
    ]

    middleware = HtmlSignpostingMiddleware(lambda request: response)
    response = middleware(None)
    content = response.content.decode("utf-8")
    assert '<link href="http://example.com" rel="author"/>' in content

def test_middleware_signposting_without_head():
    response = HttpResponse("<html><body></body></html>")
    response.status_code = 200
    response._signposts = [
        Signpost(LinkRel.author, "http://example.com")
    ]

    middleware = HtmlSignpostingMiddleware(lambda request: response)
    response = middleware(None)
    content = response.content.decode("utf-8")
    assert '<link href="http://example.com" rel="author"/>' in content


def test_middleware_multiple_signposts():
    response = HttpResponse("<html><head></head><body></body></html>")
    response.status_code = 200
    response._signposts = [
        Signpost(LinkRel.author, "http://example.com"),
        Signpost(LinkRel.author, "http://example2.com"),
        Signpost(LinkRel.cite_as, "http://example3.com"),
    ]

    middleware = HtmlSignpostingMiddleware(lambda request: response)
    response = middleware(None)
    content = response.content.decode("utf-8")
    soup = BeautifulSoup(content, "html.parser")
    assert len(soup.find_all("link")) == 3


def test_middleware_signpost_with_content_type():
    response = HttpResponse("<html><head></head><body></body></html>")
    response.status_code = 200
    response._signposts = [
        Signpost(LinkRel.item, "http://example.com", "text/json")
    ]

    middleware = HtmlSignpostingMiddleware(lambda request: response)
    response = middleware(None)
    content = response.content.decode("utf-8")
    soup = BeautifulSoup(content, "html.parser")
    assert len(soup.find_all("link")) == 1


def test_middleware_ignore_error_responses():
    response = HttpResponse("<html><head></head><body></body></html>")
    response.status_code = 400
    response._signposts = [
        Signpost(LinkRel.author, "http://example.com")
    ]

    middleware = HtmlSignpostingMiddleware(lambda request: response)
    response = middleware(None)
    content = response.content.decode("utf-8")
    soup = BeautifulSoup(content, "html.parser")
    assert len(soup.find_all("link")) == 1


def test_middleware_type_link():
    response = HttpResponse("<html><head></head><body></body></html>")
    response.status_code = 200
    response._signposts = [
        Signpost(LinkRel.type, "http://schema.org/Dataset")
    ]

    middleware = HtmlSignpostingMiddleware(lambda request: response)
    response = middleware(None)
    content = response.content.decode("utf-8")
    soup = BeautifulSoup(content, "html.parser")
    assert len(soup.find_all("link")) == 1

