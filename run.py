from enum import Enum
from uuid import uuid4
from datetime import datetime

import pandas as pd
from rdflib import BNode, SOSA

from src import value, create_uriref, insert_data
from src.graph import create_graph
from src.jsonld_context import jsonld_context
from src.models import (
    MaterialSample,
    Point,
    Procedure,
    RDFDataset,
    Sampling,
    Person,
    Sample,
    Attribute,
    SiteVisit,
    Text,
    Observation,
    TimeInstant,
    Taxon,
    Site,
)
from src.namespaces import EX, BDR_CV

transform_single_record = False

g = create_graph()

csv_filename = "records-2021-12-01.csv"

df = pd.read_csv(csv_filename)


class StateOrTerritory(Enum):
    WA = "http://linked.data.gov.au/dataset/asgs2016/stateorterritory/5"


for i, row in df.iterrows():

    # If debug is on, only process the data in the third row.
    if transform_single_record and i != 1:
        continue

    ### RDFDataset (Record)

    attr_country_code = Attribute(
        id=BNode().n3(),
        attribute=BDR_CV["country-code"],
        has_simple_value=value(row["countryCode"]),
        has_value=Text(id=BNode().n3(), value=value(row["countryCode"])),
    )

    attr_provenance = Attribute(
        id=BNode().n3(),
        attribute=BDR_CV["provenance"],
        has_simple_value=value(row["provenance"]),
        has_value=Text(id=BNode().n3(), value=value(row["provenance"])),
    )

    record = RDFDataset(
        id=EX[str(uuid4())],
        identifier=value(row["catalogNumber"]),
        license="https://creativecommons.org/licenses/by/4.0/",
        subject=BDR_CV[create_uriref(row["collectionCode"])],
        source="https://doi.org/10.26197/ala.26fdc11f-107e-45fa-9aab-3aead9083137",
        rights_holder="https://museum.wa.gov.au/",
        has_attribute=[attr_country_code, attr_provenance],
        comment="Equivalent to dwc:Record.",
    )

    ### End RDFDataset (Record)

    recorded_by = Person(
        id=BNode().n3(), name=value(row["recordedBy"]), in_dataset=record
    )

    event_date = value(row["eventDate"])
    if event_date:
        occurrence_sampling_datetime = event_date
    else:
        verbatim_event_date = value(row["verbatimEventDate"]).split("/")
        occurrence_sampling_datetime = datetime.fromisoformat(
            f"{verbatim_event_date[2]}-{verbatim_event_date[1]}-{verbatim_event_date[0]}"
        ).isoformat()

    ### Site

    site_establishment_uri = EX[str(uuid4())]
    site_uri = EX[str(uuid4())]

    site_point = Point(
        id=BNode().n3(),
        lat=value(row["decimalLatitude"]),
        long=value(row["decimalLongitude"]),
        as_wkt=f"POINT({value(row['decimalLongitude'])} {value(row['decimalLatitude'])})",
        elevation=str(value(row["verbatimElevation"])).replace(" ", "").replace("m", "")
        if value(row["verbatimElevation"])
        else None,
        has_metric_spatial_accuracy=value(row["coordinateUncertaintyInMeters"]),
    )

    site = Site(
        id=site_uri,
        feature_type="http://linked.data.gov.au/def/tern-cv/5bf7ae21-a454-440b-bdd7-f2fe982d8de4",
        identifier=site_uri,
        is_sample_of=StateOrTerritory.WA.value,
        is_result_of=site_establishment_uri,
        location_description=value(row["locationRemarks"]),
        in_dataset=record,
        has_geometry=site_point,
    )

    site_establishment = Sampling(
        id=site_establishment_uri,
        comment="Site establishment",
        has_feature_of_interest=site,
        was_associated_with=recorded_by,
        used_procedure=EX["site-establishment-method"],
        result_time=occurrence_sampling_datetime,
        has_result=site,
        in_dataset=record,
    )

    site_visit = SiteVisit(
        id=EX[str(uuid4())],
        started_at_time=occurrence_sampling_datetime,
        has_site=site,
        in_dataset=record,
    )

    insert_data({**jsonld_context, **site.dict(by_alias=True)}, g)
    insert_data({**jsonld_context, **site_establishment.dict(by_alias=True)}, g)
    insert_data({**jsonld_context, **site_visit.dict(by_alias=True)}, g)

    ### End Site

    ### Occurrence sampling

    occurrence_sampling_id = EX[str(uuid4())]

    occurrence = Sample(
        id=EX[str(uuid4())],
        identifier=value(row["occurrenceID"]),
        comment="occurrence",
        is_sample_of=site,
        is_result_of=occurrence_sampling_id,
        feature_type="http://linked.data.gov.au/def/tern-cv/2361dea8-598c-4b6f-a641-2b98ff199e9e",
        in_dataset=record,
    )

    occurrence_sampling = Sampling(
        id=occurrence_sampling_id,
        identifier=value(row["fieldNumber"]),
        has_feature_of_interest=site,
        sampling_type=BDR_CV[create_uriref(value(row["samplingProtocol"]))]
        if value(row["samplingProtocol"])
        else None,
        sf_within=[
            "https://sws.geonames.org/2077456/",
            StateOrTerritory.WA.value,
        ],
        result_time=occurrence_sampling_datetime,
        comment=value(row["locationRemarks"]),
        was_associated_with=recorded_by,
        has_result=occurrence,
        used_procedure=EX["occurrence-method"],
        in_dataset=record,
    )

    ### End of occurrence sampling

    ### Specimen sampling

    specimen_sampling_id = EX[str(uuid4())]

    specimen = MaterialSample(
        id=EX[str(uuid4())],
        comment="specimen",
        is_sample_of=occurrence.id,
        is_result_of=specimen_sampling_id,
        feature_type="http://linked.data.gov.au/def/tern-cv/cd5cbdbb-07d9-4a5b-9b11-5ab9d6015be6",
        in_dataset=record,
    )

    specimen_sampling = Sampling(
        id=specimen_sampling_id,
        used_procedure=Procedure(
            id=EX["specimen-sampling"], description=value(row["preparations"])
        ),
        result_time=occurrence_sampling_datetime,
        was_associated_with=recorded_by,
        has_result=specimen,
        has_feature_of_interest=occurrence,
        in_dataset=record,
    )

    ### End of specimen sampling

    ### Occurrence observations

    if value(row["sex"]):
        sex_observation = Observation(
            id=EX[str(uuid4())],
            comment="Sex of the occurrence.",
            in_dataset=record,
            was_associated_with=recorded_by,
            has_feature_of_interest=occurrence,
            has_simple_result=value(row["sex"]),
            has_result=Text(id=BNode().n3(), value=value(row["sex"])),
            observed_property="http://linked.data.gov.au/def/tern-cv/05cbf534-c233-4aa8-a08c-00b28976ed36",
            phenomenon_time=TimeInstant(
                id=BNode().n3(), date_timestamp=occurrence_sampling_datetime
            ),
            result_time=occurrence_sampling_datetime,
            used_procedure=BDR_CV["occurrence-method"],
        )

        insert_data({**jsonld_context, **sex_observation.dict(by_alias=True)}, g)

    life_stage_observation = Observation(
        id=EX[str(uuid4())],
        comment="life stage of the occurrence.",
        in_dataset=record,
        was_associated_with=recorded_by,
        has_feature_of_interest=occurrence,
        has_simple_result=value(row["lifeStage"]),
        has_result=Text(id=BNode().n3(), value=value(row["lifeStage"])),
        observed_property="http://linked.data.gov.au/def/tern-cv/abb0ee19-b2e8-42f3-8a25-d1f39ca3ebc3",
        phenomenon_time=TimeInstant(
            id=BNode().n3(), date_timestamp=occurrence_sampling_datetime
        ),
        result_time=occurrence_sampling_datetime,
        used_procedure=BDR_CV["occurrence-method"],
    )

    insert_data({**jsonld_context, **life_stage_observation.dict(by_alias=True)}, g)

    habitat_observation = Observation(
        id=EX[str(uuid4())],
        comment="habitat of the occurrence.",
        in_dataset=record,
        was_associated_with=recorded_by,
        has_feature_of_interest=occurrence,
        has_simple_result=value(row["habitat"]),
        has_result=Text(id=BNode().n3(), value=value(row["habitat"])),
        observed_property="http://linked.data.gov.au/def/tern-cv/2090cfd9-8b6b-497b-9512-497456a18b99",
        phenomenon_time=TimeInstant(
            id=BNode().n3(), date_timestamp=occurrence_sampling_datetime
        ),
        result_time=occurrence_sampling_datetime,
        used_procedure=BDR_CV["occurrence-method"],
    )

    insert_data({**jsonld_context, **habitat_observation.dict(by_alias=True)}, g)

    ### End of occurrence observations

    ### Specimen observations

    identified_by = Person(
        id=BNode().n3(), name=value(row["identifiedBy"]), in_dataset=record
    )

    if value(row["typeStatus"]):
        specimen_type_status_observation = Observation(
            id=EX[str(uuid4())],
            comment="speciment type status",
            in_dataset=record,
            was_associated_with=identified_by,
            has_feature_of_interest=specimen,
            has_simple_result=value(row["typeStatus"]),
            has_result=Text(id=BNode().n3(), value=value(row["typeStatus"])),
            observed_property="http://linked.data.gov.au/def/bdr-cv/specimen-type-status",
            phenomenon_time=TimeInstant(
                id=BNode().n3(),
                date_timestamp=datetime.fromisoformat(
                    f"{value(row['dateIdentified'])}-01-01"
                ).isoformat(),
            ),
            result_time=datetime.fromisoformat(
                f"{value(row['dateIdentified'])}-01-01"
            ).isoformat(),
            used_procedure=BDR_CV["specimen-method"],
        )

        insert_data(
            {**jsonld_context, **specimen_type_status_observation.dict(by_alias=True)},
            g,
        )

    specimen_taxon_result_id = BNode().n3()
    specimen_observation = Observation(
        id=EX[str(uuid4())],
        comment="specimen taxonomic information",
        in_dataset=record,
        was_associated_with=identified_by,
        has_feature_of_interest=specimen,
        has_simple_result=specimen_taxon_result_id,
        has_result=Taxon(
            id=specimen_taxon_result_id,
            in_dataset=record,
            taxon_concept_id=value(row["taxonConceptID"]),
            scientific_name=value(row["scientificName"]),
            kingdom=value(row["kingdom"]),
            phylum=value(row["phylum"]),
            class_=value(row["class"]),
            order=value(row["order"]),
            family=value(row["family"]),
            genus=value(row["genus"]),
            specific_epithet=value(row["specificEpithet"]),
            taxon_rank=value(row["taxonRank"]),
            scientific_name_authorship=value(row["scientificNameAuthorship"]),
            species=value(row["species"]),
        ),
        observed_property="http://linked.data.gov.au/def/tern-cv/70646576-6dc7-4bc5-a9d8-c4c366850df0",
        phenomenon_time=TimeInstant(
            id=BNode().n3(),
            date_timestamp=datetime.fromisoformat(
                f"{value(row['dateIdentified'])}-01-01"
            ).isoformat(),
        ),
        result_time=datetime.fromisoformat(
            f"{value(row['dateIdentified'])}-01-01"
        ).isoformat(),
        used_procedure=BDR_CV["specimen-method"],
    )

    new_jsonld_context = {**jsonld_context}
    new_jsonld_context["@context"][SOSA.hasSimpleResult] = {"@type": "@id"}
    insert_data({**new_jsonld_context, **specimen_observation.dict(by_alias=True)}, g)

    ### End of specimen observations

    insert_data(
        {
            **jsonld_context,
            **occurrence_sampling.dict(by_alias=True),
        },
        g,
    )
    insert_data(
        {
            **jsonld_context,
            **specimen_sampling.dict(by_alias=True),
        },
        g,
    )

if transform_single_record:
    g.serialize("output-row-2.ttl")
else:
    g.serialize("output.ttl")
