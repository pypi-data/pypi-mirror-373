import os
from datetime import datetime
from typing import Union

import requests
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import DCTERMS, PROV, RDF, XSD


def query_sop_sparql(named_graph_uri, query, update=False):
    """
    Perform read and write SPARQL queries against a Surround Ontology Platform (SOP) instance
    :param named_graph_uri: the graph to write to within SOP, using it's internal name e.g.
    "urn:x-evn-master:test-datagraph"
    :param query: SPARQL query to send to the SPARQL endpoint
    :param update: update = write
    :return: HTTP response
    """

    endpoint = os.environ.get("SOP_BASE_URI", "http://localhost:8083")
    username = os.environ.get("SOP_USR", "Administrator")
    password = os.environ.get("SOP_PWD", "")

    global saved_session_cookies
    with requests.session() as s:
        s.get(endpoint + "/tbl")
        reuse_sessions = False
        # should be able to check the response contains
        if reuse_sessions and saved_session_cookies:
            s.cookies = saved_session_cookies
        else:
            s.post(
                endpoint + "/tbl/j_security_check",
                {"j_username": username, "j_password": password},
            )
            # detect success!
            if reuse_sessions:
                saved_session_cookies = s.cookies

        data = {
            "default-graph-uri": named_graph_uri,
        }
        if update:
            data["update"] = query
            data["using-graph-uri"] = named_graph_uri
        else:
            data["query"] = query
            data["with-imports"] = "true"

        response = s.post(
            endpoint + "/tbl/sparql",
            data=data,
            headers={"Accept": "application/sparql-results+json"},
        )
        # force logout of session
        s.get(endpoint + "/tbl/purgeuser?app=edg")
        return response
        # .json() if response.text else {}


def make_sparql_insert_data(graph_uri, g):
    """Places RDF into a SPARQL INSERT DATA query"""
    nt = g.serialize(format="nt").decode()

    q = """
    INSERT DATA {{
        GRAPH <{}> {{
            {}
        }}
    }}
    """.format(
        graph_uri, nt
    )

    return q


def add_with_provenance(
    s: Union[URIRef, BNode],
    p: URIRef,
    o: Union[URIRef, BNode, Literal],
    block_uri: URIRef,
) -> Graph:
    """Creates a small graph, adds the given triple and also adds reified provenances for that triple"""
    g = Graph()
    # add the triple
    g.add((s, p, o))

    # add reified provenance
    x = BNode()
    g.add((x, RDF.type, RDF.Statement))
    g.add((x, RDF.subject, s))
    g.add((x, RDF.predicate, p))
    g.add((x, RDF.object, o))
    g.add(
        (
            x,
            DCTERMS.created,
            Literal(
                datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), datatype=XSD.dateTime
            ),
        )
    )
    g.add((x, PROV.wasAssociatedWith, block_uri))

    return g
