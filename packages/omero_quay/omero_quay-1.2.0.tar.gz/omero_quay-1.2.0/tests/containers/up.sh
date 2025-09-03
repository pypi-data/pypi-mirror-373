#!/bin/bash
set -eE
trap if_fail ERR

function if_fail () {
  echo "Script failed, killing all container and exiting"
  docker compose down -v
}

function check_dir () {
  for dir do
    if [[ ! -d $dir  ]]; then
      mkdir -p "$dir"
      chmod -R 766 "$dir"
    else
      echo "$dir already exist"
      chmod -R 766 "$dir"
    fi
  done
}

function healthcheck () {
  docker inspect --format='{{json .State.Health.Status}}' "$1"
}


cat << "EOF"
 ____    ____    ______          __            __
/\  _`\ /\  _`\ /\__  _\        /\ \          /\ \__
\ \ \L\_\ \ \L\ \/_/\ \/        \_\ \     __  \ \ ,_\    __
 \ \  _\/\ \  _ <' \ \ \        /'_` \  /'__`\ \ \ \/  /'__`\
  \ \ \/  \ \ \L\ \ \_\ \__  __/\ \L\ \/\ \L\.\_\ \ \_/\ \L\.\_
   \ \_\   \ \____/ /\_____\/\_\ \___,_\ \__/.\_\\ \__\ \__/.\_\
    \/_/    \/___/  \/_____/\/_/\/__,_ /\/__/\/_/ \/__/\/__/\/_/

EOF

for arg in "$@"; do
  shift
  case "$arg" in
    '--web')    set -- "$@" '-w'   ;;
    '--down')   set -- "$@" '-d'   ;;
    '--purge')  set -- "$@" '-p'   ;;
    *)          set -- "$@" "$arg" ;;
  esac
done

up_omeroweb=false
url="https://zenodo.org/records/15789629/files/data.tar.gz?download=1"

OPTIND=1
while getopts ':wdp' OPTION; do
  case "$OPTION" in
    'w')
      up_omeroweb=true
      ;;
    'd')
      docker compose down
      exit
      ;;
    'p')
      docker compose down -v
      exit
      ;;
    '?')
      echo "Usage:
        $(basename "$0") : Launch docker env without omero-web
        $(basename "$0") [-w --web] : Launch docker env with omero-web
        $(basename "$0") [-d --down] : shutdown docker env
        $(basename "$0") [-p --purge] : Purge docker env including images and volumes" >&2
      exit 1
      ;;
  esac
done
# shellcheck disable=SC2004
shift "$(($OPTIND -1))"

if [ -z "${QUAY_TEST_DATA}" ]; then
  export QUAY_TEST_DATA="./QuayTestData"
  echo "QUAY_TEST_DATA not set, defaulting to $QUAY_TEST_DATA"
fi

if [ -z "${CI_COMMIT_BRANCH}" ]; then
  export CI_COMMIT_BRANCH="dev"
  echo "CI_COMMIT_BRANCH not set, defaulting to $CI_COMMIT_BRANCH"
fi


# Check if needed dir exists
check_dir "$QUAY_TEST_DATA"

if [[ -z $(ls -A "$QUAY_TEST_DATA") ]]; then
  curl -L "$url" | tar -xz -C "$QUAY_TEST_DATA"/..
fi
chmod -R 777 "$QUAY_TEST_DATA"

# standup irods
# docker compose pull --quiet irods-icat
# docker compose pull --quiet irods-db
docker compose up -d --no-build irods-icat

# Wait for irods container before creating users
# sleep 5 for CI
echo "Waiting until iRods server is healthy..."
until healthcheck irods-icat = "healthy"; do sleep 1; done
echo "iRods server started"

until
  docker exec -u irods irods-icat iadmin lu;
do
  echo "Retrying..."
  sleep 10;
done

sleep 10

if docker exec -u irods irods-icat iadmin lu | grep omero-server; then
  echo "iRods user omero-server already exist..."
  docker exec -u irods irods-icat iadmin moduser omero-server password omero-root-password;
else
  echo "Creating iRods user omero-server..."
  until
    docker exec -u irods irods-icat iadmin mkuser omero-server rodsadmin;
  do
    sleep 1;
    echo "Retrying...";
  done
  docker exec -u irods irods-icat iadmin moduser omero-server password omero-root-password
fi


docker compose up -d --no-build irods-consumer

if docker exec -u irods irods-icat ilsresc | grep mesoUserResc; then
  echo "Icat Resc already exists..."
else
  echo "Creating resources in irods-icat"
  until
      docker exec -u root irods-icat chown -R irods:irods /mnt/user;
      docker exec -u irods irods-icat iadmin mkresc \
             mesoUserResc unixfilesystem irods-icat:/mnt/user;
  do
    echo "Retrying...";
  done
fi

if docker exec -u irods irods-icat ilsresc | grep mesoCoopResc; then
  echo "Icat Resc already exists..."
else
  echo "Creating resources in irods-icat"
  until
      docker exec -u root irods-icat chown -R irods:irods /mnt/coop;
      docker exec -u irods irods-icat iadmin mkresc \
             mesoCoopResc unixfilesystem irods-icat:/mnt/coop;
  do
    echo "Retrying...";
  done
fi

if docker exec -u irods irods-consumer ilsresc | grep facilityFileResc; then
  echo "Facility Resc already exists..."
else
  echo "Creating resources in irods-consumer"
  until
      docker exec -u root irods-consumer chown -R irods:irods /mnt/user;
      docker exec -u irods irods-consumer iadmin mkresc \
             facilityUserResc unixfilesystem irods-consumer:/mnt/user;
  do
    echo "Retrying...";
  done
fi

if docker exec -u irods irods-consumer ilsresc | grep facilityCoopResc; then
  echo "Facility Resc already exists..."
else
  echo "Creating resources in irods-consumer"
  until

      docker exec -u root irods-consumer chown -R irods:irods /mnt/coop;
      docker exec -u irods irods-consumer iadmin mkresc \
             facilityCoopResc unixfilesystem irods-consumer:/mnt/coop;
  do
    echo "Retrying...";
  done
fi
docker exec -u irods irods-icat imkdir /tempZone/home/investigations
docker exec -u irods irods-icat ichmod -r own omero-server /tempZone/home/investigations

# standup nfsrods
docker compose up -d nfsrods

# standup omero
docker compose up -d --no-build omero-server

echo "Waiting until Omero server is healthy..."
sleep 10
until healthcheck omero-server = "healthy"; do sleep 1; done
echo "Omero server started"

sleep 10


docker compose up -d mongo

until
  docker exec -u omero-server omero-server /opt/omero/server/OMERO.server/bin/omero user list -s localhost -u root -w omero
do
  sleep 3
done

echo "Omero server started"


echo "Mount NFSrods volume on omero-server"
docker exec -u root omero-server mount -t nfs -o \
  "rw,intr,soft,noatime,tcp,timeo=14,nolock,nfsvers=4" \
  nfsrods:/home /mnt/SHARE

# shellcheck disable=SC2034
if up_omeroweb=true; then
  docker compose up -d omero-web
fi

docker compose up -d quay-facility
docker exec quay-facility mkdir /mnt/user/home
docker exec quay-facility cp -R /tmp/QuayTestData/facility0 /mnt/user/home/
