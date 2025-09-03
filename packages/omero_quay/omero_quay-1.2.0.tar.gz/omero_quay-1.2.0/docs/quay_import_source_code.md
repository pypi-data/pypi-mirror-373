# Quay Import source code components

Quay Import is an OMERO webapp which purpose is to import microscopy data (image files + associated metadata) from local drive to an iRODS installation (see OMERO Quay config file parameters). This app is a Django project. It is composed of these files:

- "views.py": Main engine of the web app. Contains the functions.
- "urls.py": Django matchings between URLs and HTML content
- "settings.py": Django configuration parameters for good functioning
- "static": This directory contains resources for web page generation:
    - "app.css": CSS elements for items disposition and behaviour on page
    - "assets": This directory contains web page images and icons 
- "templates": This directory contains the HTML docs to build the web page body.
    - "quay_import/index.html": Main page body
    - "quay_import/manifest.html": Excel file importation YAML manifest elements

## Views.py file

:::quay_import.views