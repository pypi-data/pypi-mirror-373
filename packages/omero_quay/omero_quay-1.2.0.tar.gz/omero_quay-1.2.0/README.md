# omero-quay

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]

[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

<!-- prettier-ignore-start -->
[actions-link]:             https://gitlab.in2p3.fr/fbi-data/omero-quay/badges/main/pipeline.svg
[pypi-link]:                https://pypi.org/project/omero-quay/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/omero-quay
[pypi-version]:             https://img.shields.io/pypi/v/omero-quay
[rtd-badge]:                https://readthedocs.org/projects/omero-quay/badge/?version=latest
[rtd-link]:                 https://omero-quay.readthedocs.io/en/latest/?badge=latest
<!-- prettier-ignore-end -->

`omero-quay` is a microscopy data transport layer between data management tools.

Currently, it supports the [iRODS](https://irods.org) —
[OMERO](https://openmicroscopy.org/omero) architecture built at France
BioImaging [fbi-omero](https://gitlab.in2p3.fr/fbi-data/fbi-omero).

![omero-quay orchestrate data transport between iRODS and OMERO](docs/services-architecture.svg)

## Objectives

- Interact with data management tools APIs
- Trigger actions:
  - Create / Read / Update / Delete
  - Transport / Import
- Synch databases :warning:

## Schema driven development

- [`manifest.yml`](src/schema/manifest-schema.yml) defines the data schema in
  LinkML
- follows an Investigation Study Assay hierarchy
- maps APIs, objects ids, ACLs
- **only transports "crates", not individual files**

### Generate the pydantic classes:

```sh
gen-pydantic src/omero_quay/schema/manifest-schema.yml --template-dir=src/omero_quay/templates  > src/omero_quay/core/manifest.py
```

## ZeroMQ

![](docs/message_flows.svg){ width="70%" }

- Message = json dump of a `manifest` instance
- Central brocker routes messages based on **state**

## Example route:

![](docs/import_route.svg){ width="60%" }

# Install

This is early stage and only meant for developers.

For now, install from source.

1. Get and install a `conda` distribution. We prefer
   [micromamba](https://mamba.org/micromamba)
2. Download omero-quay from this repository (as an archive or with git)
3. In the `omero-quay` directory:
   - create the conda environment `conda env create -f environment.yml`
   - activate it `conda activate quay`
   - install `omero-quay` in editable mode `pip install -e .[dev]`

For now, this software alone is not very useful, and works only within the
`omero-fbi` frameworks. Work on setting up a `docker compose` view of this
format is in the works. Look into the [`tests`](tests) folder for examples.

# Configuration

The configuration is described in [quay.yml](src/omero-quay/core/quay.yml). On
the client or server machine, adapt this file and copy it to
`/home/user/.config/quay.yml`

# Usage

## Remote client

### Install

- Install omero-quay (see above)
- add irods server IP to /etc/hosts
- Write the client configuration file and save it to `$HOME/.config/quay.yml`

```yaml
---
irods:
  # This is the configuration for Montpellier
  IRODS_HOST: irods-mtp.omero-fbi.fr
ingest:
  POST_URL: https://mtp.omero-fbi.fr/post
```

### Import data

(all paths below are relative to the omero-quay root directory where this
`README` file resides)

- Put an excel file with the relevant data at the root of the directory you want
  to import

- Run the import client (make sure the `quay` environment is activated):

```sh

python scripts/desktop_cli.py other/path/to/your.xlsx path_in_irods
```

## Service

On the OMERO server machine:

```sh
python scripts/run_service.py
```

## Excel client

On a client machine

```sh
python scripts/excel_import.py
```

## Autoingest with iRODS

TODO

# Tests

In order to run tests, you need to boot up docker containers for the omero
server, irods catalog provider and nfsrods.

This is achieved by running `up.sh` script in `tests/containers`

```sh
cd tests/containers
./up.sh

```

After some minutes and possible connection retries, you should have the
containers running.

You can then run the tests from the root of the repo with `pytest`
