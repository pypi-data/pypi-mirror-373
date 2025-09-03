FROM continuumio/miniconda3:main

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git unzip
RUN useradd -ms /bin/bash omero-facility

COPY install_quay.sh /tmp/install_quay.sh
RUN chown omero-facility:omero-facility /tmp/install_quay.sh


USER omero-facility
RUN chmod +x /tmp/install_quay.sh && /tmp/install_quay.sh

USER root
RUN mkdir /mnt/user
RUN chown omero-facility:omero-facility /mnt/user

RUN mkdir /mnt/coop
RUN chown omero-facility:omero-facility /mnt/coop

USER omero-facility
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
