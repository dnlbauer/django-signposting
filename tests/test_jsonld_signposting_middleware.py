import json
from django.http import HttpRequest, HttpResponse

from django_signposting.middleware import JsonLdSignpostingParserMiddleware
from signposting import Signpost, LinkRel


def jsonld_test_runner(jsonld, expected_signposts):
    response = HttpResponse(f"""
    <html><head>
    <script type="application/ld+json">{json.dumps(jsonld)}</script>
    </head>
    <body></body>
    </html>
    """)
    response.status_code = 200

    middleware = JsonLdSignpostingParserMiddleware(lambda request: response)
    response = middleware(HttpRequest())

    for expected_signpost in expected_signposts:
        assert expected_signpost in response._signposts

    assert len(expected_signposts) == len(response._signposts)


def test_jsonld_signposting_basic():
    jsonld_test_runner(
        {
            "@context": "http://schema.org",
            "@type": "WebPage",
            "author": {"url": "http://example.com/author"},
            "url": "http://example.com/url",
            "license": {"identifier": "http://example.com/license"},
            "hasPart": [
                {
                    "url": "http://example.com/image1.jpg",
                },
                {
                    "url": "http://example.com/image2.jpg",
                },
            ],
            "sameAs": [
                {
                    "url": "http://example.com/metadata.json",
                },
                {
                    "url": "http://example.com/metadata.xml",
                },
            ],
        },
        [
            Signpost(LinkRel.type, "http://schema.org/WebPage"),
            Signpost(LinkRel.author, "http://example.com/author"),
            Signpost(LinkRel.cite_as, "http://example.com/url"),
            Signpost(LinkRel.license, "http://example.com/license"),
            Signpost(LinkRel.item, "http://example.com/image1.jpg"),
            Signpost(LinkRel.item, "http://example.com/image2.jpg"),
            Signpost(LinkRel.describedby, "http://example.com/metadata.json"),
            Signpost(LinkRel.describedby, "http://example.com/metadata.xml"),
        ],
    )


def test_jsonld_empty_signposting():
    jsonld_test_runner({}, [])


def test_jsonld_signposting_media_types():
    jsonld_test_runner(
        {
            "@context": "http://schema.org",
            "@type": "WebPage",
            "author": {"url": "http://example.com/author"},
            "url": "http://example.com/url",
            "license": {"identifier": "http://example.com/license"},
            "hasPart": [
                {
                    "url": "http://example.com/image1.jpg",
                    "encodingFormat": "image/jpeg",
                },
                {"url": "http://example.com/image2.jpg", "encodingFormat": "image/png"},
            ],
            "sameAs": [
                {
                    "url": "http://example.com/metadata.json",
                    "encodingFormat": "application/json",
                },
                {
                    "url": "http://example.com/metadata.xml",
                    "encodingFormat": "application/xml",
                },
            ],
        },
        [
            Signpost(LinkRel.type, "http://schema.org/WebPage"),
            Signpost(LinkRel.author, "http://example.com/author"),
            Signpost(LinkRel.cite_as, "http://example.com/url"),
            Signpost(LinkRel.license, "http://example.com/license"),
            Signpost(LinkRel.item, "http://example.com/image1.jpg", "image/jpeg"),
            Signpost(LinkRel.item, "http://example.com/image2.jpg", "image/png"),
            Signpost(
                LinkRel.describedby,
                "http://example.com/metadata.json",
                "application/json",
            ),
            Signpost(
                LinkRel.describedby,
                "http://example.com/metadata.xml",
                "application/xml",
            ),
        ],
    )


def test_jsonld_signposting_property_precedence():
    jsonld_test_runner(
        {
            "@context": "http://schema.org",
            "@type": "WebPage",
            "author": {
                "identifier": "http://example.com/author-ident",
                "url": "http://example.com/author-url",
            },
            "hasPart": [
                {
                    "identifier": "http://example.com/image1-identifier.jpg",
                    "url": "http://example.com/image1-url.jpg",
                    "contentUrl": "http://example.com/image1-content.jpg",
                },
                {
                    "identifier": "http://example.com/image2-identifier.jpg",
                    "url": "http://example.com/image2-url.jpg",
                },
            ],
        },
        [
            Signpost(LinkRel.type, "http://schema.org/WebPage"),
            Signpost(LinkRel.author, "http://example.com/author-url"),
            Signpost(LinkRel.item, "http://example.com/image1-content.jpg"),
            Signpost(LinkRel.item, "http://example.com/image2-url.jpg"),
        ],
    )


def test_jsonld_signposting_ids():
    jsonld_test_runner(
        {
            "@context": "http://schema.org",
            "@graph": [
                {
                    "@type": "WebPage",
                    "author": {"@id": "http://example.com/author"},
                    "url": "http://example.com/url",
                    "license": {"@id": "http://example.com/license"},
                    "hasPart": [
                        {
                            "@id": "http://example.com/image1.jpg",
                        },
                    ],
                    "sameAs": [
                        {
                            "@id": "http://example.com/metadata.json",
                        },
                    ],
                },
                {"@id": "http://example.com/author", "@type": "Person"},
                {"@id": "http://example.com/license"},
                {
                    "@id": "http://example.com/image1.jpg",
                    "encodingFormat": "image/jpeg",
                },
                {"@id": "http://example.com/metadata.json"},
            ],
        },
        [
            Signpost(LinkRel.type, "http://schema.org/WebPage"),
            Signpost(LinkRel.author, "http://example.com/author"),
            Signpost(LinkRel.cite_as, "http://example.com/url"),
            Signpost(LinkRel.license, "http://example.com/license"),
            Signpost(LinkRel.item, "http://example.com/image1.jpg", "image/jpeg"),
            Signpost(LinkRel.describedby, "http://example.com/metadata.json"),
        ],
    )


def test_jsonld_signposting_ids_with_url():
    jsonld_test_runner(
        {
            "@context": "http://schema.org",
            "@graph": [
                {
                    "@type": "WebPage",
                    "author": {"@id": "http://example.com/author"},
                },
                {
                    "@id": "http://example.com/author",
                    "url": "http://example.com/realAuthorUrl",
                },
            ],
        },
        [
            Signpost(LinkRel.type, "http://schema.org/WebPage"),
            Signpost(LinkRel.author, "http://example.com/realAuthorUrl"),
        ],
    )


def test_jsonld_signposting_multiple_types():
    jsonld_test_runner(
        {
            "@context": "http://schema.org",
            "@type": "Dataset",
            "author": "http://example.com/author",
        },
        [
            Signpost(LinkRel.type, "http://schema.org/Dataset"),
            Signpost(LinkRel.author, "http://example.com/author"),
        ],
    )
