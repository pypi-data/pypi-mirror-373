FROM openmicroscopy/omero-server:5.6.16

USER root

RUN dnf install -y nfs-utils
RUN mkdir /mnt/SHARE && chown -R omero-server:omero-server /mnt/SHARE

ADD 90-quay_server.sh /startup/
RUN chown -R omero-server:omero-server /startup/ && chmod -R u+x /startup/

ADD install_quay.sh .
RUN chown omero-server:omero-server install_quay.sh && chmod u+x install_quay.sh

USER omero-server
RUN ./install_quay.sh
WORKDIR /opt/setup

EXPOSE 4063 4064
ENV PATH=$PATH:/opt/ice/bin

VOLUME ["/OMERO", "/opt/omero/server/OMERO.server/var"]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
