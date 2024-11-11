from django.http import HttpResponse
from django.views import View
from django.shortcuts import render

from django_json_ld.views import JsonLdContextMixin
from django_signposting.utils import add_signposts

from signposting import Signpost, LinkRel


class SimpleView(View):

    def get(self, request):
        response = HttpResponse("Hello, world!")

        # Add signpostings as string
        add_signposts(
            response,
            Signpost(LinkRel.type, "http://schema.org/Dataset"),
            Signpost(LinkRel.author, "https://orcid.org/0000-0001-9447-460X")
        )

        return response


class JsonLdView(JsonLdContextMixin, View):

    sd = {
        "@context": "https://schema.org",
        "@type": ["WebSite", "Dataset"],
        "name": "My Dataset",
        "description": "A dataset of things.",
        "url": "https://example.com",
        "sameAs": [
            {
                "@type": "MediaObject",
                "contentUrl": "https://example.com/download.zip",
                "encodingFormat": "application/zip"
            },
            {
                "@type": "MediaObject",
                "contentUrl": "https://example.com/metadata.json",
            }
        ],
        "author": {
            "@type": "Person",
            "name": "Daniel Bauer",
            "url": "https://orcid.org/0000-0001-9447-460X",
        },
        "license": {
            "@type": "CreativeWork",
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/"
        },
        "hasPart": [
            {
                "@type": "ImageObject",
                "url": "http://example.com/image.png",
                "encodingFormat": "image/png"
            },
            {
                "@type": "ImageObject",
                "url": "http://example.com/image2.png",
                "encodingFormat": "image/png"
            }
        ]
    }

    def get(self, request):
        return render(request, "jsonld.html", context={"sd": self.sd})
