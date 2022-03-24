# ALA Darwin Core worked examples

The data was obtained from ALA. Here is the [DOI](https://doi.org/10.26197/ala.26fdc11f-107e-45fa-9aab-3aead9083137) to the data.

This repository contains a worked example of converting ALA data from Darwin Core to the TERN Ontology.

A mapping spreadsheet of the data to the RDF terms in the TERN Ontology.

## Worked example

The source data downloaded from ALA is the [records-2021-12-01.csv](records-2021-12-01.csv) file.

A mapping spreadsheet was created to map the columns of the CSV file to the TERN Ontology.

The [run.py](run.py) script is used to convert the CSV file to RDF.

- [Mapped Faealla spreadsheet](https://docs.google.com/spreadsheets/d/1p3scX7z6wPQ0vtG-Bo_yoYcvRRs8muGm/edit?usp=sharing&ouid=108129827562056706312&rtpof=true&sd=true)

## Visualising the RDF data in Ontodia

View the data in Ontodia at https://ternaustralia.github.io/bdr-faealla-worked-example.

## Conceptual modelling assumptions

The worked example was created based on the following assumptions:

- Each row in the CSV file represents a Darwin Core record. These records are represented in the TERN Ontology with the class `tern:RDFDataset`.
- All items in a row (observation, sampling, etc.) are part of an `tern:RDFDataset` instance.
- The provenance and country code information are recorded in the `tern:RDFDataset` class as `tern:Attribute` instances.
- Sites are inferred from the location remarks and the decimal latitude and longitude values.
- Occurrences are recorded with the class `tern:Sampling`. The sampling events take place from within the established site. The result of the sampling is an occurrence recorded as a `tern:Sample`.
- The person who performed the samplings and observations also established the site.
- Three possible observations are made on the occurrence (fauna) sample:
  - sex (gender) of the occurrence
  - life stage of the occurrence
  - habitat description of the occurrence
- A specimen of an occurrence is recorded with the class `tern:MaterialSample`. The way the specimen was collected are recorded with the class `tern:Sampling`.
- Two possible observations are made on the specimen:
  - type status
  - taxonomic information (captured with the `tern:Taxon`)
- Attribution to people are recorded with the property `prov:wasAssociatedWith`.

## Contact

Edmond Chuc  
e.chuc@uq.edu.au
