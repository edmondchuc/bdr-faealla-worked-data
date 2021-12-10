from enum import Enum
from uuid import uuid4
from datetime import datetime

import pandas as pd
from rdflib import BNode

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
    Text,
    Observation,
    TimeInstant,
)
from src.namespaces import EX, BDR_CV

transform_single_record = True

g = create_graph()

csv_filename = "records-2021-12-01.csv"

df = pd.read_csv(csv_filename)


class StateOrTerritory(Enum):
    WA = "http://linked.data.gov.au/dataset/asgs2016/stateorterritory/5"


for i, row in df.iterrows():

    # If debug is on, only process the data in the third row.
    if transform_single_record and i != 2:
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

    ### Occurrence sampling

    occurrence_sampling_point = Point(
        id=BNode().n3(),
        lat=value(row["decimalLatitude"]),
        long=value(row["decimalLongitude"]),
        as_wkt=f"POINT({value(row['decimalLongitude'])} {value(row['decimalLatitude'])})",
        elevation=str(value(row["verbatimElevation"])).replace(" ", "").replace("m", "")
        if value(row["verbatimElevation"])
        else None,
        coordinate_uncertainty=value(row["coordinateUncertaintyInMeters"]),
    )

    event_date = value(row["eventDate"])
    if event_date:
        occurrence_sampling_datetime = event_date
    else:
        verbatim_event_date = value(row["verbatimEventDate"]).split("/")
        occurrence_sampling_datetime = datetime.fromisoformat(
            f"{verbatim_event_date[2]}-{verbatim_event_date[1]}-{verbatim_event_date[0]}"
        ).isoformat()

    occurrence_sampling_id = EX[str(uuid4())]

    occurrence = Sample(
        id=EX[str(uuid4())],
        identifier=value(row["occurrenceID"]),
        comment="occurrence",
        is_sample_of=StateOrTerritory.WA.value,
        is_result_of=occurrence_sampling_id,
        feature_type="http://linked.data.gov.au/def/tern-cv/2361dea8-598c-4b6f-a641-2b98ff199e9e",
        in_dataset=record,
    )

    occurrence_sampling = Sampling(
        id=occurrence_sampling_id,
        identifier=value(row["fieldNumber"]),
        has_feature_of_interest=StateOrTerritory.WA.value,
        sampling_type=BDR_CV[create_uriref(value(row["samplingProtocol"]))]
        if value(row["samplingProtocol"])
        else None,
        has_geometry=occurrence_sampling_point,
        sf_within=[
            "https://sws.geonames.org/2077456/",
            StateOrTerritory.WA.value,
        ],
        result_time=occurrence_sampling_datetime,
        comment=value(row["locationRemarks"]),
        was_associated_with=Person(id=BNode().n3(), name=value(row["recordedBy"])),
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
            id=BNode().n3(), description=value(row["preparations"])
        ),
        result_time=occurrence_sampling_datetime,
        was_associated_with=Person(id=BNode().n3(), name=value(row["recordedBy"])),
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
            was_associated_with=Person(id=BNode().n3(), name=value(row["recordedBy"])),
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
        was_associated_with=Person(id=BNode().n3(), name=value(row["recordedBy"])),
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
        was_associated_with=Person(id=BNode().n3(), name=value(row["recordedBy"])),
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

    ### End of occurrence observations

    ### Specimen observations

    # TODO:

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

g.serialize("output.ttl")
