from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django_json_ld.views import JsonLdContextMixin
from signposting import LinkRel, Signpost

from django_signposting.utils import add_signposts, jsonld_to_signposts


class SimpleView(View):
    """ A simple view that adds signposting headers to the response."""

    def get(self, request):
        response = HttpResponse("Hello, world!")

        # Add signpostings as string
        add_signposts(
            response,
            Signpost(LinkRel.type, "http://schema.org/Dataset"),
            Signpost(LinkRel.author, "https://orcid.org/0000-0001-9447-460X"),
        )

        return response


class JsonLdView(JsonLdContextMixin, View):
    """ A view that automatically adds signposting headers to the response based on
    the JSON-LD metadata in the response."""

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
                "encodingFormat": "application/zip",
            },
            {
                "@type": "MediaObject",
                "contentUrl": "https://example.com/metadata.json",
            },
        ],
        "author": {
            "@type": "Person",
            "name": "Daniel Bauer",
            "url": "https://orcid.org/0000-0001-9447-460X",
        },
        "license": {
            "@type": "CreativeWork",
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
        },
        "hasPart": [
            {
                "@type": "ImageObject",
                "url": "http://example.com/image.png",
                "encodingFormat": "image/png",
            },
            {
                "@type": "ImageObject",
                "url": "http://example.com/image2.png",
                "encodingFormat": "image/png",
            },
        ],
    }

    def get(self, request):
        return render(request, "jsonld.html", context={"sd": self.sd})


class rocrate(JsonLdContextMixin, View):
    """ A view that adds signposting headers from the metadata of a detached RO-Crate."""

    def get(self, request):
        import json
        import os
        import tempfile

        # Build an RO-Crate and serve its preview
        from rocrate.model.person import Person
        from rocrate.model.creativework import CreativeWork
        from rocrate.rocrate import ROCrate

        with tempfile.TemporaryDirectory() as d:
            crate = ROCrate(gen_preview=True)
            crate.add_file(
                "http://example.com/test.pdf",
                properties={"name": "test file", "encodingFormat": "application/pdf"},
            )
            author = crate.add(
                Person(
                    crate,
                    "https://orcid.org/0000-0001-9447-460X",
                    properties={"name": "Daniel Bauer"},
                )
            )
            license = crate.add(
                CreativeWork(
                    crate,
                    "https://spdx.org/licenses/CC0-1.0",
                    properties={
                        "@id": "https://spdx.org/licenses/CC0-1.0",
                        "@type": "CreativeWork",
                        "name": "CC0-1.0",
                        "description": "Creative Commons Zero v1.0 Universal",
                    },
                )
            )
            sameAs = crate.add(
                CreativeWork(
                    crate,
                    "https://example.com/ro-crate-metadata.json",
                    properties={"encodingFormat": "application/ld+json"},
                )
            )

            crate.root_dataset["name"] = "My Dataset"
            crate.root_dataset["description"] = "A dataset of things."
            crate.root_dataset["author"] = author
            crate.root_dataset["creator"] = author
            crate.root_dataset["license"] = license
            crate.root_dataset["url"] = "https://example.com"
            crate.root_dataset["sameAs"] = sameAs
            crate.write(d)

            # Extract JSON-LD from RO-Crate metadata and build signposts from it
            metadata = open(os.path.join(d, "ro-crate-metadata.json"), "r").read()
            metadata = json.loads(metadata)
            signposts = jsonld_to_signposts(metadata)

            preview = open(os.path.join(d, "ro-crate-preview.html"), "r").read()
            response = HttpResponse(preview)
            add_signposts(response, *signposts)
            return response
