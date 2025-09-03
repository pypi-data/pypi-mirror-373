FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
        apt-transport-https \
        gnupg \
        wget \
        gettext

RUN useradd -s /bin/bash -d /var/lib/irods irods

RUN wget -qO - https://packages.irods.org/irods-signing-key.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.irods.org/apt/ jammy main" | tee /etc/apt/sources.list.d/renci-irods.list

ARG irods_version=4.3.4
ARG irods_package_version_suffix="-0~jammy"
ARG irods_package_version=${irods_version}${irods_package_version_suffix}

RUN apt-get update && \
    apt-get install -y \
        libcurl4-gnutls-dev \
        python3 \
        python3-distro \
        python3-jsonschema \
        python3-pip \
        python3-venv \
        python3-jinja2 \
        python3-psutil \
        python3-requests \
        rsyslog \
        unixodbc \
        netcat-openbsd \
        net-tools \
        irods-database-plugin-postgres=${irods_package_version} \
        irods-runtime=${irods_package_version} \
        irods-server=${irods_package_version} \
        irods-icommands=${irods_package_version} \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/*

COPY server_config.tpl entrypoint.sh template_jinja.py /tmp/
RUN chmod u+x /tmp/entrypoint.sh
ENTRYPOINT ["/tmp/entrypoint.sh"]
