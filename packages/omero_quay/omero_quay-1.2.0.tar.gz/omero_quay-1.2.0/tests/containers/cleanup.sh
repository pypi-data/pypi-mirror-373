#! /usr/bin/bash

set -xeu
docker compose down
docker volume rm containers_irods-data
docker volume rm containers_irods-db
docker volume rm containers_omero-data
docker volume rm containers_omero-db
