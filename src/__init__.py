import json
from urllib.parse import quote_plus

import pandas as pd
from rdflib import URIRef, Graph
from rdflib.term import _is_valid_uri


def value(cell):
    if pd.isna(cell):
        return None
    return cell


def create_uriref(uri):
    """Create a URIRef with the same validation func used by URIRef"""
    if _is_valid_uri(uri):
        return URIRef(uri)
    return URIRef(quote_plus(uri))


def insert_data(data: dict, graph: Graph):
    graph.parse(data=json.dumps(data), format="json-ld")
