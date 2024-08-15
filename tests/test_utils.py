from django.http import HttpResponse
from django_signposting.utils import add_signposts


def test_add_signpost():
    response = HttpResponse()
    add_signposts(response, item="http://example.com")

    assert response._signposts["item"] == ["http://example.com"]


def test_add_multiple_signposts():
    response = HttpResponse()
    add_signposts(response,
                  item="http://example.com",
                  author=["https://example2.com", "https://example3.com"]
                  )

    assert response._signposts == {
        "item": ["http://example.com"],
        "author": [
            "https://example2.com",
            "https://example3.com",
        ]
    }


def test_add_signposts_with_content_type():
    response = HttpResponse()
    add_signposts(response,
                  item=("http://example.com", "text/json"),
                  author=["https://example2.com", "https://example3.com"]
                  )

    assert response._signposts == {
        "item": [("http://example.com", "text/json")],
        "author": [
            "https://example2.com",
            "https://example3.com",
        ]
    }


def test_add_signposts_from_dict():
    response = HttpResponse()
    add_signposts(response, **{"cite-as": ["https://example.com"]})
    assert response._signposts["cite-as"] == ["https://example.com"]
