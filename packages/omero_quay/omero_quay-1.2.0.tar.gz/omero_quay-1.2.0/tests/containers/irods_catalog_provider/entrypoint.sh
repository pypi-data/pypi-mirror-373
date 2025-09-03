#! /bin/bash -e

template_file=/tmp/server_config.tpl
setup_input_file=/tmp/server_config.json
install_checker=/var/lib/irods/.installed

mkdir -p $IRODS_RES_DIR
chown -R irods:irods /var/lib/irods /etc/irods $IRODS_RES_DIR

if [ -f "${template_file}" ] && [ ! -f "${install_checker}" ]; then
    echo "Templating setup file"
    python3 /tmp/template_jinja.py "${setup_input_file}" "${template_file}" 

    echo "Running iRODS setup"
    su irods -c '/var/lib/irods/scripts/setup_irods.py -v \
      --json_configuration_file /tmp/server_config.json \
      && touch /var/lib/irods/.installed'
fi

echo "Starting server"

cd /usr/sbin
su irods -c 'bash -c "./irodsServer -u"'
