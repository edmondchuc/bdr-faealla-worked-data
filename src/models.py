from typing import Optional, List, Union

from pydantic import BaseModel, Field
from rdflib import DCTERMS, SOSA, RDFS, SDO, PROV, VOID, RDF, TIME

from src.namespaces import GEO, WGS, TERN_LOC, TERN, DWC, SF


class Base(BaseModel):
    id: str = Field(alias="@id")
    type: str = Field(alias="@type")
    in_dataset: Optional["RDFDataset"] = Field(alias=VOID.inDataset)

    class Config:
        allow_population_by_field_name = True


class Value(Base):
    type: str = Field(TERN.Value, alias="@type")


class Taxon(Value):
    type: str = Field(TERN.Taxon, alias="@type")
    taxon_concept_id: str = Field(alias=DWC.taxonConceptID)
    scientific_name: str = Field(alias=DWC.scientificName)
    kingdom: str = Field(alias=DWC.kingdom)
    phylum: str = Field(alias=DWC.phylum)
    class_: str = Field(alias=DWC["class"])
    order: str = Field(alias=DWC.order)
    family: str = Field(alias=DWC.family)
    genus: str = Field(alias=DWC.genus)
    specific_epithet: str = Field(alias=DWC.specificEpithet)
    taxon_rank: str = Field(alias=DWC.taxonRank)
    scientific_name_authorship: str = Field(alias=DWC.scientificNameAuthorship)
    species: str = Field(alias=DWC.species)


class Text(Value):
    type: str = Field(TERN.Text, alias="@type")
    value: str = Field(alias=RDF.value)


class Attribute(Base):
    type: str = Field(TERN.Attribute, alias="@type")
    attribute: str = Field(alias=TERN.attribute)
    has_value: Union[str, Value] = Field(alias=TERN.hasValue)
    has_simple_value: str = Field(alias=TERN.hasSimpleValue)


class RDFDataset(Base):
    type: str = Field(TERN.RDFDataset, alias="@type")
    identifier: str = Field(alias=DCTERMS.identifier)
    license: str = Field(alias=DCTERMS.license)
    subject: str = Field(alias=DCTERMS.subject)
    source: str = Field(alias=DCTERMS.source)
    rights_holder: str = Field(alias=DCTERMS.rightsHolder)
    has_attribute: Union[Union[str, Attribute], List[Union[str, Attribute]]] = Field(
        alias=TERN.hasAttribute
    )
    comment: str = Field(alias=RDFS.comment)


class Agent(Base):
    name: str = Field(alias=SDO.name)
    type: str = Field(PROV.Agent, alias="@type")


class Person(Agent):
    type: str = Field(SDO.Person, alias="@type")


class Geometry(Base):
    type: str = Field(GEO.Geometry, alias="@type")
    as_wkt: str = Field(alias=GEO.asWKT)
    elevation: Optional[str] = Field(alias=TERN_LOC.elevation)
    has_metric_spatial_accuracy: str = Field(alias=GEO.hasMetricSpatialAccuracy)


class Point(Geometry):
    type: str = Field(SF.Point, alias="@type")
    lat: str = Field(alias=WGS.lat)
    long: str = Field(alias=WGS.long)
    elevation: Optional[str] = Field(alias=TERN_LOC.elevation)
    has_metric_spatial_accuracy: str = Field(alias=GEO.hasMetricSpatialAccuracy)


class Procedure(Base):
    type: str = Field(SOSA.Procedure, alias="@type")
    description: str = Field(alias=DCTERMS.description)


class Activity(Base):
    has_feature_of_interest: Union[str, "FeatureOfInterest"] = Field(
        alias=SOSA.hasFeatureOfInterest
    )
    was_associated_with: Person = Field(alias=PROV.wasAssociatedWith)
    used_procedure: Union[str, Procedure] = Field(alias=SOSA.usedProcedure)
    has_geometry: Optional[Geometry] = Field(alias=GEO.hasGeometry)
    sf_within: Optional[List[str]] = Field(alias=GEO.sfWithin)
    result_time: str = Field(alias=SOSA.resultTime)
    comment: Optional[str] = Field(alias=RDFS.comment)


class Sampling(Activity):
    type: str = Field(TERN.Sampling, alias="@type")
    identifier: Optional[str] = Field(alias=DCTERMS.identifier)
    sampling_type: Optional[str] = Field(alias=TERN.samplingType)
    has_result: "Sample" = Field(alias=SOSA.hasResult)


class TimeInstant(Base):
    type: str = Field(TERN.Instant, alias="@type")
    date_timestamp: Optional[str] = Field(alias=TIME.inXSDDateTimeStamp)
    date: Optional[str] = Field(alias=TIME.inXSDDate)


class Observation(Activity):
    type: str = Field(TERN.Observation, alias="@type")
    has_result: Value = Field(alias=SOSA.hasResult)
    has_simple_result: str = Field(alias=SOSA.hasSimpleResult)
    observed_property: str = Field(alias=SOSA.observedProperty)
    phenomenon_time: TimeInstant = Field(alias=SOSA.phenomenonTime)


class FeatureOfInterest(Base):
    feature_type: str = Field(alias=TERN.featureType)


class Sample(FeatureOfInterest):
    type: str = Field(TERN.Sample, alias="@type")
    identifier: str = Field(alias=DCTERMS.identifier)
    comment: Optional[str] = Field(alias=RDFS.comment)
    is_sample_of: Union[str, "Sample"] = Field(alias=SOSA.isSampleOf)
    is_result_of: Union[str, Sampling] = Field(alias=SOSA.isResultOf)
    has_geometry: Optional[Geometry] = Field(alias=GEO.hasGeometry)


class Site(Sample):
    type: str = Field(TERN.Site, alias="@type")
    sf_within: Optional[List[str]] = Field(alias=GEO.sfWithin)
    location_description: str = Field(alias=TERN.locationDescription)


class SiteVisit(Base):
    type: str = Field(TERN.SiteVisit, alias="@type")
    started_at_time: str = Field(alias=PROV.startedAtTime)
    has_site: Site = Field(alias=TERN.hasSite)


class MaterialSample(Sample):
    type: str = Field(TERN.MaterialSample, alias="@type")
    identifier: Optional[str] = Field(alias=DWC.materialSampleID)


FeatureOfInterest.update_forward_refs()
Sampling.update_forward_refs()
Sample.update_forward_refs()
MaterialSample.update_forward_refs()
Observation.update_forward_refs()
Taxon.update_forward_refs()
Person.update_forward_refs()
Site.update_forward_refs()
SiteVisit.update_forward_refs()
