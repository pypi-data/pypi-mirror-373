all: docker_pull docker_up docker_info test docker_down

test:
	cd tests/containers && \
		docker compose run --rm quay-client bash -c "cd /home/omero-facility/omero-quay && /home/omero-facility/.conda/envs/quay/bin/python -m pytest"
omero_logs:
	docker exec -it  omero-server bash -c "tail -f /opt/omero/server/log/omero_quay/main.log"

pydantic_classes:
	gen-pydantic src/omero_quay/schema/manifest-schema.yml \
		--template-dir=src/omero_quay/templates > \
		src/omero_quay/core/manifest.py

client_bash:
	cd tests/containers && \
		docker compose run --rm quay-client bash

docker_omero_logs:
	docker exec omero-server tail -f /opt/omero/server/log/omero_quay/main.log

docker_up:
	cd tests/containers && ./up.sh

docker_down:
	cd tests/containers && ./up.sh --down

docker_purge:
	cd tests/containers && ./up.sh --purge

restart_all: docker_purge docker_up docker_populate

restart_omero:
	cd tests/containers && ./restart_omero.sh


docker_reset_inv:
	docker exec -u irods irods-icat  \
	    ils /tempZone/home/JCB2009/
	docker exec -u irods -e clientUserName=facility0 irods-icat\
	    irm -r /tempZone/home/JCB2009/Figure1
	docker exec -u irods -e clientUserName=facility0 irods-icat\
	    irm -r /tempZone/home/JCB2009/Figure2
	docker exec -u irods -e clientUserName=facility0 irods-icat\
	    irm -r /tempZone/home/JCB2009/Figure3
	docker exec -u irods -e clientUserName=facility0 irods-icat\
	    irm -r /tempZone/home/JCB2009/Figure4
	docker exec -u irods -e clientUserName=facility0 irods-icat\
	    irm -r /tempZone/home/JCB2009/Figure5
	docker exec -u irods -e clientUserName=facility0 irods-icat\
	    irm -r /tempZone/home/JCB2009/Figure6
	docker exec -u irods irods-icat  \
	    iadmin rmgroup JCB2009

docker_populate:
	docker exec omero-server /tmp/populate_omero.sh
	docker exec -u root irods-icat bash -c "chown irods:irods /tmp/populate_irods.sh"
	docker exec -u root irods-icat bash -c "chmod +x /tmp/populate_irods.sh"
	docker exec -u irods irods-icat  /tmp/populate_irods.sh
	docker exec -u irods irods-icat  \
	    ichmod -r own omero-server /tempZone/
	docker exec -u root irods-icat chown 1001:1001 /tmp/populate_irods.sh

docker_pull:
	cd tests/containers && docker compose pull --quiet

archive_tests:
	tar -cvzf data.tar.gz $QUAY_TEST_DATA/QuayTestData
