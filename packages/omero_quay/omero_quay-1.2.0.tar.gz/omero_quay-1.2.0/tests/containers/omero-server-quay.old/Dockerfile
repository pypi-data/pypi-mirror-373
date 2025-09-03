FROM rockylinux:9
LABEL maintainer="ome-devel@lists.openmicroscopy.org.uk"

RUN dnf -y install epel-release
RUN dnf -y update
RUN dnf install -y glibc-langpack-en
RUN dnf install -y blosc

ARG CI_COMMIT_BRANCH
ENV CI_COMMIT_BRANCH=${CI_COMMIT_BRANCH}

ENV LANG en_US.utf-8
ENV RHEL_FRONTEND=noninteractive
RUN mkdir /opt/setup
WORKDIR /opt/setup
ADD playbook.yml requirements.yml /opt/setup/

RUN dnf install -y ansible-core sudo ca-certificates
RUN ansible-galaxy install -p /opt/setup/roles -r requirements.yml
RUN dnf -y clean all
RUN rm -fr /var/cache

ARG OMERO_VERSION=5.6.10
ARG OMEGO_ADDITIONAL_ARGS=
ENV OMERODIR=/opt/omero/server/OMERO.server

RUN ansible-playbook playbook.yml -vvv -e 'ansible_python_interpreter=/usr/bin/python3'\
    -e omero_server_release=$OMERO_VERSION \
    -e omero_server_omego_additional_args="$OMEGO_ADDITIONAL_ARGS" \
    -e HTTPS_PROXY="$HTTPS_PROXY" \
    -e HTTP_PROXY="$HTTP_PROXY"

RUN dnf install -y mount.nfs procps net-tools
RUN mkdir /mnt/SHARE

RUN dnf -y clean all
RUN rm -fr /var/cache

RUN curl -L -o /usr/local/bin/dumb-init \
    https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_x86_64 && \
    chmod +x /usr/local/bin/dumb-init

ADD entrypoint.sh /usr/local/bin/
RUN chown -R omero-server:omero-server /usr/local/bin/entrypoint.sh
RUN chmod -R u+x /usr/local/bin/entrypoint.sh
ADD 50-config.py 60-database.sh 99-run.sh 90-quay_server.sh /startup/
RUN chown -R omero-server:omero-server /startup/
RUN chmod -R u+x /startup/

ADD install_quay.sh .
RUN chown omero-server:omero-server install_quay.sh
RUN chmod u+x install_quay.sh

USER omero-server
RUN echo $CI_COMMIT_BRANCH
RUN ./install_quay.sh
WORKDIR /opt/setup

EXPOSE 4063 4064
ENV PATH=$PATH:/opt/ice/bin

VOLUME ["/OMERO", "/opt/omero/server/OMERO.server/var"]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
