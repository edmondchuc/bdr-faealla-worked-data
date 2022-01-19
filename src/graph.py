from rdflib import Graph, DCTERMS, SOSA, PROV, SDO, VOID, TIME

from src.namespaces import EX, TERN, TERN_LOC, GEO, WGS, DWC, SF


def create_graph():
    g = Graph()
    g.bind("ex", EX)
    g.bind("tern", TERN)
    g.bind("tern-loc", TERN_LOC)
    g.bind("geo", GEO)
    g.bind("wgs", WGS)
    g.bind("dcterms", DCTERMS)
    g.bind("sosa", SOSA)
    g.bind("prov", PROV)
    g.bind("sdo", SDO)
    g.bind("dwc", DWC)
    g.bind("void", VOID)
    g.bind("time", TIME)
    g.bind("sf", SF)
    return g
