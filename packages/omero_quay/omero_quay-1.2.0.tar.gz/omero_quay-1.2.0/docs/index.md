# Documentation OMERO Quay

## Guidelines

`omero-quay` is a microscopy data transport layer between data management tools (currently OMERO and iRODS) and file systems (currently SAMBA and SRB (iRODS specific file system)).

Currently, it supports the [iRODS](https://irods.org) — [OMERO](https://openmicroscopy.org/omero) architecture built at France BioImaging [fbi-omero](https://gitlab.in2p3.fr/fbi-data/fbi-omero).

![omero-quay orchestrate data transport between iRODS and OMERO](images/services-architecture.svg)

OMERO quay has different purposes depending on how you intend to use it, so the next sections will be divided according to the users expected profiles:

- System administrator: self-explanatory
- Advanced user: no administration tasks, but intend to import data. Possibly limited to scripts usage (see Scripts subsection in Code section)
- Developer: new functions coding, possible scripts development

[How to use](how_to_use.md){:target="_blank"}

[Installation and deployment](installation_and_deployment.md){:target="_blank"}

[Configuration file (quay.yml) content](configuration_file_content.md){:target="_blank"}

## Code

[OMERO Quay source code](omero_quay_source_code.md){:target="_blank"}

[OMERO Quay scripts](omero_quay_scripts.md){:target="_blank"}

[Quay Import source code](quay_import_source_code.md){:target="_blank"}


