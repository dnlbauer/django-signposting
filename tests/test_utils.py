from django.http import HttpResponse
from django_signposting.utils import add_signposts
from signposting import Signpost, LinkRel


def test_add_signpost():
    response = HttpResponse()
    add_signposts(response, Signpost(LinkRel.item, "http://example.com"))

    assert len(response._signposts) == 1


def test_add_multiple_signposts():
    response = HttpResponse()
    add_signposts(response,
                  Signpost(LinkRel.item, "http://example.com"),
                  Signpost(LinkRel.author, "https://example2.com"),
                  Signpost(LinkRel.author, "https://example3.com"),
                  )

    assert len(response._signposts) == 3


def test_add_signpost_call_multiple_times():
    response = HttpResponse()
    add_signposts(response, Signpost(LinkRel.item, "http://example.com"))
    add_signposts(response, Signpost(LinkRel.item, "http://example2.com"))

    assert len(response._signposts) == 2


def test_add_signpost_duplicate():
    response = HttpResponse()
    add_signposts(response, Signpost(LinkRel.item, "http://example.com"))
    add_signposts(response, Signpost(LinkRel.item, "http://example.com"))

    assert len(response._signposts) == 1
