from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from jinja2 import Environment, PackageLoader
from linkml_runtime.dumpers import json_dumper
from rocrate_validator import models, services

from omero_quay.core.connect import omero_conn
from omero_quay.core.manifest import Assay, Investigation, Manifest, Study
from omero_quay.core.provenance import (
    get_data_root,
)
from omero_quay.core.utils import find_by_id
from omero_quay.managers.manager import Manager
from omero_quay.rocrate.vignette_generator import (
    OmeroVignetteFetcher,
    VignetteGenerator,
)

log = logging.getLogger(__name__)

SRC_DIR = Path(__file__).parent.parent.resolve()


jinja_env = Environment(
    loader=PackageLoader("omero_quay"),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)

templates = SRC_DIR / "templates"
icons = SRC_DIR / "icons"

rocrate_template_path = templates / "ro-crate-metadata.json.j2"
html_template_path = templates / "html_rocrate_main_page_template.j2"
index_template_path = templates / "ro-crate-preview.html.j2"


investigation_icon_path = icons / "investigation.svg"
study_icon_path = icons / "study.svg"
assay_icon_path = icons / "assay.svg"


class RoCrateManager(Manager):
    """
    Generate RO-Crate metadata and preview for each investigation in the manifest
    """

    def __init__(self, conf: dict, manifest: Manifest, data_path=None):
        super().__init__(conf, manifest, scheme=None, host=os.uname().nodename)
        self.log.info("initiating rocrate")
        self.log.info("Manifest: " + str(self.manifest.id))
        self.log.info("Target store: " + str(self.trgt_store))
        self.conf = conf
        self.manifest = manifest
        self.matching_investigation = self.manifest.investigations[0].name
        self.json_manifest = None
        if data_path is None:
            self.data_path = Path(
                get_data_root(self.manifest, self.trgt_store.id, template=True)
            )
        else:
            self.data_path = Path(data_path)
        if omero_conn(self.conf) is not None:
            self.omero_flag = True
        else:
            self.omero_flag = False
        self.log.info("Data path: " + str(self.data_path))
        self.investigation_path = self.data_path / self.matching_investigation
        self.log.info("Investigation path: " + str(self.investigation_path))
        self.rocrate_output = None
        self.rocrate_filename = "ro-crate-metadata.json"
        self.rocrate_path = self.investigation_path / self.rocrate_filename
        self.log.info("Rocrate path: " + str(self.rocrate_path))
        self.html_output = None
        self.html_filename = "rocrate_index_preview.html"
        self.html_path = self.investigation_path / self.html_filename
        self.log.info("HTML path: " + str(self.html_path))
        self.log.info("Going to routine")

    def routine(self, dry=False):
        self.log.info(
            "Started step %i / %i", self.manifest.step + 1, len(self.manifest.route)
        )
        if not dry:
            self.crud()
            self.validate_rocrate_file()  # takes several minutes
            self.log.info("finished ro-crate")
            for state in self.manifest.states:
                self.log.info("\t %s : %s", state.store, state.status)
                if state.status == "errored":
                    break
                if state.store == self.trgt_store.id:
                    continue
                if state.status in ("checked", "changed"):
                    continue
                state.status = "expired"

        self.manifest.step += 1
        self.log.info(
            "Finished step %i / %i", self.manifest.step, len(self.manifest.route)
        )

        if self.manifest.error is not None:
            self.log.error(
                "Got an error in manifest %s: %s",
                self.manifest.id,
                self.manifest.error,
            )
            self.set_state("errored")
        return json_dumper.dumps(self.manifest)

    def crud(self):
        self.log.info("Started Ro-Crate CRUD")

        # self.render_json_manifest()
        # json_manifest_filepath = self.investigation_path / "manifest.json"
        # with json_manifest_filepath.open("w", encoding="utf-8") as manifest_content:
        # manifest_content.write(self.json_manifest)

        self.render_rocrate_json_string()
        self.rocrate_output = json.loads(self.rocrate_string)
        self.create_vignettes_from_manifest()
        with self.rocrate_path.open("w", encoding="utf-8") as rocrate_file:
            rocrate_file.write(str(self.rocrate_output).replace("'", '"'))

        self.render_rocrate_html_file()
        with self.html_path.open("w", encoding="utf-8") as rocrate_html:
            rocrate_html.write(self.html_output)

        if self.state.status == "changed":
            self.set_state("checked")
            return
        self.set_state("changed")

    def render_rocrate_json_string(self):
        """
        Creates the rocrate JSON content which serves as a data file to construct the final rocrate webpage.
        Uses manifest as source.
        """
        template = jinja_env.get_template("ro-crate-metadata.json.j2")
        self.rocrate_string = template.render(
            filename=self.rocrate_filename,
            manifest=self.manifest,
            investigation=self.manifest.investigations[0],
        )

    """
    def render_json_manifest(self):
        self.json_manifest = json_dumper.dumps(self.manifest)
    """

    def make_vignette(self, rocrate_item, image):
        self.log.info("Image: " + str(image))
        assay = find_by_id(image.parents[-1], self.manifest.assays)
        self.log.info("Assay: %s", assay.name)
        item_directory = self.absolute_path(assay, self.trgt_store.id)
        item_path = item_directory / image.name
        if self.omero_flag is True:
            """
            Gets the matching image vignette from OMERO. To be tested once images implemented in manifest.
            """
            item_vignette_generator = OmeroVignetteFetcher(
                item_path, self.conf, image.ome_id
            )
            item_vignette_generator.fetch_and_save_omero_vignette()
        else:
            """
            Creates a vignette with my own functions. To be tested once images implemented in manifest.
            """
            item_vignette_generator = VignetteGenerator(item_path)
            item_vignette_generator.save_image_as_gif()
        if rocrate_item["name"] == image.name:
            rocrate_item["thumbnailUrl"] = str(item_vignette_generator.vignette_path)

    def create_vignettes_from_manifest(self):
        """
        Create vignettes and add information about the vignettes in the rocrate JSON file.
        Regenerate an updated JSON content.
        """
        self.log.info("Creating vignettes")
        # self.log.info("ISA_items: " + str(self.isaobjects))
        # self.log.info("Images: " + str(self.manifest.images))
        for rocrate_item in self.rocrate_output["@graph"]:
            # self.log.info("RO-Crate item: " + str(rocrate_item))
            if str(rocrate_item["@type"]) == "Dataset":
                for isaobject in self.isaobjects:
                    if str(rocrate_item["name"]) == str(isaobject.name):
                        if isinstance(isaobject, Investigation):
                            rocrate_item["thumbnailUrl"] = str(investigation_icon_path)
                        if isinstance(isaobject, Study):
                            rocrate_item["thumbnailUrl"] = str(study_icon_path)
                        if isinstance(isaobject, Assay):
                            rocrate_item["thumbnailUrl"] = str(assay_icon_path)
            if str(rocrate_item["@type"]) == "File":
                for item in self.manifest.images:
                    if str(rocrate_item["name"]) == str(item.name):
                        self.log.info("Creating vignette for " + str(item.name))
                        self.make_vignette(rocrate_item, item)
            # self.log.info("RO-Crate item AFTER: " + str(rocrate_item))

    def render_rocrate_html_file(self):
        """
        Creates the HTML rocrate webpage content.
        Uses generated rocrate JSON as source.
        """
        template = jinja_env.get_template("ro-crate-preview.html.j2")
        self.html_output = template.render(
            filename=self.html_filename, input=self.rocrate_output
        )

    def find_rocrate_item(self, isaobject):
        """
        Finds ro-crate item from manifest ISA object
        """
        for rocrate_item in self.rocrate_output["@graph"]:
            if rocrate_item["name"] == isaobject.name:
                return rocrate_item
        return None

    def validate_rocrate_file(self):
        """
        Validates ro-crate file using Python rocrate_validator library.
        """
        # Create an instance of `ValidationSettings` class to configure the validation
        settings = services.ValidationSettings(
            # Set the path to the RO-Crate root directory
            rocrate_uri=str(self.investigation_path),
            # Set the identifier of the RO-Crate profile to use for validation.
            # If not set, the system will attempt to automatically determine the appropriate validation profile.
            profile_identifier="ro-crate-1.1",
            # Set the requirement level for the validation
            requirement_severity=models.Severity.REQUIRED,
        )

        # Call the validation service with the settings
        result = services.validate(settings)

        # Check if the validation was successful
        if not result.has_issues():
            log.info("RO-Crate is valid!")
            return True
        log.info("RO-Crate is invalid!")
        # Explore the issues
        for issue in result.get_issues():
            # Every issue object has a reference to the check that failed, the severity of the issue, and a message describing the issue.
            log.info(
                f'Detected issue of severity {issue.severity.name} with check "{issue.check.identifier}": {issue.message}'
            )
        return False
