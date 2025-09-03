#!/bin/bash
set -eE
trap if_fail ERR


docker restart omero-server
until
  docker exec -u omero-server omero-server /opt/omero/server/OMERO.server/bin/omero user list -s localhost -u root -w omero
do
  sleep 3
done

echo "Omero server restarted"

echo "Mount NFSrods volume on omero-server"
docker exec -u root omero-server mount -t nfs -o \
  "rw,intr,soft,noatime,tcp,timeo=14,nolock,nfsvers=4" \
  nfsrods:/home /mnt/SHARE

echo "restarting quay-facility"
docker restart quay-facility
