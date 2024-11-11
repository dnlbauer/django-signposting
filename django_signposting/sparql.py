from rdflib import Graph
from rdflib.query import Result


def root_element_query(g: Graph) -> Result:
    return g.query("""
PREFIX schema: <http://schema.org/>

SELECT DISTINCT ?rootElement
WHERE {
  # has a type
  ?rootElement a ?type ;
  # has a license or an author or a creator
  (schema:license | schema:author | schema:creator ) ?value .

  # No incoming edges for ?rootElement
  FILTER NOT EXISTS { ?s ?p ?rootElement }

}
LIMIT 1
""")


def type_query(g: Graph, rootElement: str) -> Graph:
    return g.query(
        """
PREFIX schema: <?context>

SELECT DISTINCT ?type
WHERE {
  ?rootElement a ?type .
}
""",
        initBindings={"rootElement": rootElement},
    )


def author_query(g: Graph, rootElement: str):
    return g.query(
        """
PREFIX schema: <http://schema.org/>

SELECT ?author_id ?identifier ?url
WHERE {
    ?rootElement schema:author ?author .

    BIND(?author AS ?author_id)  # Get the @id of the author
    OPTIONAL { ?author schema:identifier ?identifier }
    OPTIONAL { ?author schema:url ?url }
}
LIMIT 1
""",
        initBindings={"rootElement": rootElement},
    )


def license_query(g: Graph, rootElement: str):
    return g.query(
        """
PREFIX schema: <http://schema.org/>

SELECT ?element_id ?identifier ?url
WHERE {
    ?rootElement schema:license ?element .

    BIND(?element AS ?element_id)  # Get the @id of the element
    OPTIONAL { ?element schema:identifier ?identifier }
    OPTIONAL { ?element schema:url ?url }
}
LIMIT 1
""",
        initBindings={"rootElement": rootElement},
    )


def cite_query(g: Graph, rootElement: str):
    return g.query(
        """
PREFIX schema: <http://schema.org/>

SELECT ?element_id ?identifier ?url
WHERE {
    ?rootElement schema:url ?element .

    BIND(?element AS ?element_id)  # Get the @id of the element
    OPTIONAL { ?element schema:identifier ?identifier }
    OPTIONAL { ?element schema:url ?url }
}
LIMIT 1
""",
        initBindings={"rootElement": rootElement},
    )


def sameas_query(g: Graph, rootElement: str):
    return g.query(
        """
PREFIX schema: <http://schema.org/>

SELECT ?element_id ?identifier ?url ?contentUrl ?encoding
WHERE {
    ?rootElement schema:sameAs ?element .

    BIND(?element AS ?element_id)  # Get the @id of the element
    OPTIONAL { ?element schema:contentUrl ?contentUrl }
    OPTIONAL { ?element schema:identifier ?identifier }
    OPTIONAL { ?element schema:url ?url }
    OPTIONAL { ?element schema:encodingFormat ?encoding }
}
""",
        initBindings={"rootElement": rootElement},
    )


def item_query(g: Graph, rootElement: str):
    return g.query(
        """
PREFIX schema: <http://schema.org/>

SELECT ?element_id ?identifier ?url ?contentUrl ?encoding
WHERE {
    ?rootElement schema:hasPart ?element .
    #VALUES ?element_type { schema:MediaObject schema:Dataset }
    #?element a ?element_type .

    BIND(?element AS ?element_id)  # Get the @id of the element
    OPTIONAL { ?element schema:contentUrl ?contentUrl }
    OPTIONAL { ?element schema:identifier ?identifier }
    OPTIONAL { ?element schema:url ?url }
    OPTIONAL { ?element schema:encodingFormat ?encoding }
}
""",
        initBindings={"rootElement": rootElement},
    )
