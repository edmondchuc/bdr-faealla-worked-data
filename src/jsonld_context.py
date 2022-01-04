from rdflib import XSD, SOSA, DCTERMS, TIME

from src.namespaces import TERN_LOC, WGS, GEO, TERN, DWC


jsonld_context = {
    "@context": {
        TERN_LOC.elevation: {"@type": XSD.double},
        WGS.lat: {"@type": XSD.double},
        WGS.long: {"@type": XSD.double},
        GEO.sfWithin: {"@type": "@id"},
        TERN.samplingType: {"@type": "@id"},
        SOSA.resultTime: {"@type": XSD.dateTime},
        SOSA.usedProcedure: {"@type": "@id"},
        SOSA.hasFeatureOfInterest: {"@type": "@id"},
        TERN.featureType: {"@type": "@id"},
        DCTERMS.license: {"@type": "@id"},
        TERN_LOC.coordinateUncertainty: {"@type": XSD.double},
        DCTERMS.source: {"@type": "@id"},
        DCTERMS.rightsHolder: {"@type": "@id"},
        TIME.inXSDDateTimeStamp: {"@type": XSD.dateTimeStamp},
        SOSA.observedProperty: {"@type": "@id"},
        DWC.taxonConceptID: {"@type": "@id"},
    }
}
