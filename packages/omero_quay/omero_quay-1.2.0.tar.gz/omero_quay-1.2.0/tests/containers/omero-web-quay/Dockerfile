FROM openmicroscopy/omero-web-standalone:5.29

USER root
RUN dnf install -y git nodejs python3.12 python3.12-pip
RUN rm /usr/bin/python3 && ln -s /usr/bin/python3.12 /usr/bin/python3
RUN npm install -g n
RUN chown -R omero-web:omero-web /opt/omero/web/venv3

USER omero-web

RUN python3 -m venv --upgrade /opt/omero/web/venv3
RUN /opt/omero/web/venv3/bin/python3 -m pip install --upgrade pip

# Add OMERO frontend elements
COPY ./images \
  /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/webclient/static/webclient/image/
COPY ./style/ome.login.css \
  /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/webgateway/static/webgateway/css/ome.login.css
COPY ./style/login.html \
  /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/webclient/templates/webclient/login.html

# Add custom omero-quay
WORKDIR /tmp
RUN git clone -b dev https://gitlab.in2p3.fr/fbi-data/omero-quay.git
WORKDIR /tmp/omero-quay

RUN /opt/omero/web/venv3/bin/pip install \
    wheel\
    omero_mapr\
    omero-figure\
    omero_autotag\
    omero_tagsearch\
    omero_parade\
    omero-iviewer\
    omero-weberror\
    omero_fpbioimage\
    python-irodsclient\
    pytest\
    pytest-mock\
    pyyaml\
    tables\
    pytest-django\
    whitenoise\
    https://github.com/glencoesoftware/zeroc-ice-py-linux-x86_64/releases/download/20240202/zeroc_ice-3.6.5-cp312-cp312-manylinux_2_28_x86_64.whl

RUN /opt/omero/web/venv3/bin/pip install -e .

ADD 01-default-webapps.omero /opt/omero/web/config/

VOLUME ["/opt/omero/web/OMERO.web/var"]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
