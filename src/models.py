from typing import Optional, List, Union

from pydantic import BaseModel, Field
from rdflib import DCTERMS, SOSA, RDFS, SDO, PROV, VOID, RDF, TIME

from src.namespaces import GEO, WGS, TERN_LOC, TERN, DWC, SF


class Base(BaseModel):
    id: str = Field(alias="@id")
    type: str = Field(alias="@type")
    in_dataset: Optional["RDFDataset"] = Field(alias=str(VOID.inDataset))

    class Config:
        allow_population_by_field_name = True


class Value(Base):
    type: str = Field(TERN.Value, alias="@type")


class Taxon(Value):
    type: str = Field(TERN.Taxon, alias="@type")
    taxon_concept_id: str = Field(alias=str(DWC.taxonConceptID))
    scientific_name: str = Field(alias=str(DWC.scientificName))
    kingdom: str = Field(alias=str(DWC.kingdom))
    phylum: str = Field(alias=str(DWC.phylum))
    class_: str = Field(alias=str(DWC["class"]))
    order: str = Field(alias=str(DWC.order))
    family: str = Field(alias=str(DWC.family))
    genus: str = Field(alias=str(DWC.genus))
    specific_epithet: str = Field(alias=str(DWC.specificEpithet))
    taxon_rank: str = Field(alias=str(DWC.taxonRank))
    scientific_name_authorship: str = Field(alias=str(DWC.scientificNameAuthorship))
    species: str = Field(alias=str(DWC.species))


class Text(Value):
    type: str = Field(TERN.Text, alias="@type")
    value: str = Field(alias=str(RDF.value))


class Attribute(Base):
    type: str = Field(TERN.Attribute, alias="@type")
    attribute: str = Field(alias=str(TERN.attribute))
    has_value: Union[str, Value] = Field(alias=str(TERN.hasValue))
    has_simple_value: str = Field(alias=str(TERN.hasSimpleValue))


class RDFDataset(Base):
    type: str = Field(TERN.RDFDataset, alias="@type")
    identifier: str = Field(alias=str(DCTERMS.identifier))
    license: str = Field(alias=str(DCTERMS.license))
    subject: str = Field(alias=str(DCTERMS.subject))
    source: str = Field(alias=str(DCTERMS.source))
    rights_holder: str = Field(alias=str(DCTERMS.rightsHolder))
    has_attribute: Union[Union[str, Attribute], List[Union[str, Attribute]]] = Field(
        alias=str(TERN.hasAttribute)
    )
    comment: str = Field(alias=str(RDFS.comment))


class Agent(Base):
    name: str = Field(alias=str(SDO.name))
    type: str = Field(PROV.Agent, alias="@type")


class Person(Agent):
    type: str = Field(SDO.Person, alias="@type")


class Geometry(Base):
    type: str = Field(GEO.Geometry, alias="@type")
    as_wkt: str = Field(alias=str(GEO.asWKT))
    elevation: Optional[str] = Field(alias=str(TERN_LOC.elevation))
    has_metric_spatial_accuracy: str = Field(alias=str(GEO.hasMetricSpatialAccuracy))


class Point(Geometry):
    type: str = Field(SF.Point, alias="@type")
    lat: str = Field(alias=str(WGS.lat))
    long: str = Field(alias=str(WGS.long))
    elevation: Optional[str] = Field(alias=str(TERN_LOC.elevation))
    has_metric_spatial_accuracy: str = Field(alias=str(GEO.hasMetricSpatialAccuracy))


class Procedure(Base):
    type: str = Field(SOSA.Procedure, alias="@type")
    description: str = Field(alias=str(DCTERMS.description))


class Activity(Base):
    has_feature_of_interest: Union[str, "FeatureOfInterest"] = Field(
        alias=str(SOSA.hasFeatureOfInterest)
    )
    was_associated_with: Person = Field(alias=str(PROV.wasAssociatedWith))
    used_procedure: Union[str, Procedure] = Field(alias=str(SOSA.usedProcedure))
    has_geometry: Optional[Geometry] = Field(alias=str(GEO.hasGeometry))
    sf_within: Optional[List[str]] = Field(alias=str(GEO.sfWithin))
    result_time: str = Field(alias=str(SOSA.resultTime))
    comment: Optional[str] = Field(alias=str(RDFS.comment))


class Sampling(Activity):
    type: str = Field(TERN.Sampling, alias="@type")
    identifier: Optional[str] = Field(alias=str(DCTERMS.identifier))
    sampling_type: Optional[str] = Field(alias=str(TERN.samplingType))
    has_result: "Sample" = Field(alias=str(SOSA.hasResult))


class TimeInstant(Base):
    type: str = Field(TERN.Instant, alias="@type")
    date_timestamp: Optional[str] = Field(alias=str(TIME.inXSDDateTimeStamp))
    date: Optional[str] = Field(alias=str(TIME.inXSDDate))


class Observation(Activity):
    type: str = Field(TERN.Observation, alias="@type")
    has_result: Value = Field(alias=str(SOSA.hasResult))
    has_simple_result: str = Field(alias=str(SOSA.hasSimpleResult))
    observed_property: str = Field(alias=str(SOSA.observedProperty))
    phenomenon_time: TimeInstant = Field(alias=str(SOSA.phenomenonTime))


class FeatureOfInterest(Base):
    feature_type: str = Field(alias=str(TERN.featureType))


class Sample(FeatureOfInterest):
    type: str = Field(TERN.Sample, alias="@type")
    identifier: str = Field(alias=str(DCTERMS.identifier))
    comment: Optional[str] = Field(alias=str(RDFS.comment))
    is_sample_of: Union[str, "Sample"] = Field(alias=str(SOSA.isSampleOf))
    is_result_of: Union[str, Sampling] = Field(alias=str(SOSA.isResultOf))
    has_geometry: Optional[Geometry] = Field(alias=str(GEO.hasGeometry))


class Site(Sample):
    type: str = Field(TERN.Site, alias="@type")
    sf_within: Optional[List[str]] = Field(alias=str(GEO.sfWithin))
    location_description: str = Field(alias=str(TERN.locationDescription))


class SiteVisit(Base):
    type: str = Field(TERN.SiteVisit, alias="@type")
    started_at_time: str = Field(alias=str(PROV.startedAtTime))
    has_site: Site = Field(alias=str(TERN.hasSite))


class MaterialSample(Sample):
    type: str = Field(TERN.MaterialSample, alias="@type")
    identifier: Optional[str] = Field(alias=str(DWC.materialSampleID))


FeatureOfInterest.update_forward_refs()
Sampling.update_forward_refs()
Sample.update_forward_refs()
MaterialSample.update_forward_refs()
Observation.update_forward_refs()
Taxon.update_forward_refs()
Person.update_forward_refs()
Site.update_forward_refs()
SiteVisit.update_forward_refs()
