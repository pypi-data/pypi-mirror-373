from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path

import aicsimageio
import ffmpeg
import imageio
import numpy as np
import PIL
import skimage
from aicsimageio import AICSImage

from omero_quay.core.connect import omero_conn

log = logging.getLogger(__name__)

dtype_map = {
    "uint8": np.uint8,
    "uint16": np.uint16,
    "uint32": np.uint32,
}


class OmeroVignetteFetcher:
    def __init__(self, image_path, conf, image_ome_id):
        self.image_path = image_path
        self.vignette_path = str(self.set_current_vignette_name_stub()) + ".jpg"
        self.conf = conf
        self.image_ome_id = image_ome_id

    def set_vignettes_path(self):
        if not self.image_path.exists():
            msg = f"{self.image_path} not found"
            raise ValueError(msg)
        log.info("Image path: " + str(self.image_path))
        # image_directory = self.image_path.parents[0]
        investigation_directory = self.image_path.parents[2]
        study_name = str(self.image_path.parents[1]).rsplit("/", maxsplit=1)[-1]
        assay_name = str(self.image_path.parents[0]).rsplit("/", maxsplit=1)[-1]
        vignettes_directory = (
            investigation_directory / "ro-crate-preview_files" / study_name / assay_name
        )
        log.info("Vignettes directory: " + str(vignettes_directory))
        Path(vignettes_directory).mkdir(parents=True, exist_ok=True)
        return vignettes_directory

    def set_current_vignette_name_stub(self):
        vignettes_path = self.set_vignettes_path()
        image_name = Path(self.image_path).parts[-1]
        return str(vignettes_path) + "/" + str(image_name) + "_omero_vignette"

    def fetch_and_save_omero_vignette(self):
        log.info("Image Omero_ID: " + str(self.image_ome_id))
        with omero_conn(self.conf) as conn:
            image_omero_item = conn.getObject("Image", self.image_ome_id)
            img_data = image_omero_item.getThumbnail()
        rendered_thumb = PIL.Image.open(BytesIO(img_data))
        thumbnail_path = Path(str(self.vignette_path))
        rendered_thumb.save(thumbnail_path)


class VignetteGenerator:
    def __init__(self, image_path):
        self.image_path = image_path
        self.vignette_path = str(self.set_current_vignette_name_stub()) + ".gif"
        self.vignette_numpy_array = self.vignette_pipeline()

    def get_formalism(self, aics_image):
        """
        Note from https://zenodo.org/records/4906609:

        RGB / BGR Support

        Due to the scene management changes, we no longer use the "S" dimension to represent "Scene". We use it to represent the "Samples" dimension (RGB / BGR) which means we now have an isolated dimension for color data. This is great because it allows us to directly support multi-channel RGB data, where previously we would expand RGB data into channels, even when the file had a channel dimension.
        So if you encounter a file with "S" in the dimensions, you can know that you are working with an RGB file.
        """
        log.info("Image dimensions: " + str(aics_image.dims))
        log.info("Image dimension order: " + aics_image.dims.order)
        log.info("Image dimension order type: " + str(type(aics_image.dims.order)))
        log.info("Image shape: " + str(aics_image.shape))
        if aics_image.dims.order == "TCZYX":
            target_dims_for_zprojection = "ZCTYX"
            target_dims_for_channel_fusion = "CTZYX"
        if aics_image.dims.order == "TCZYXS":
            target_dims_for_zprojection = "ZSCTYX"
            target_dims_for_channel_fusion = "CSTZYX"

        return (
            aics_image.dims.order,
            target_dims_for_zprojection,
            target_dims_for_channel_fusion,
        )

    def make_fused_channels(self, aics_image_numpy_array, source_dims, target_dims):
        """
        For cosmic rays correction, use this. Otherwise, too saturated:

            retransposed_transposed_aics_image_numpy_array = (
                retransposed_transposed_aics_image_numpy_array
                * (
                    256
                    / (
                        1
                        + np.quantile(
                            retransposed_transposed_aics_image_numpy_array, 0.99
                        )  # for cosmic rays
                        - np.quantile(retransposed_transposed_aics_image_numpy_array, 0.01)
                    )
                )
            ).astype(np.uint8)
        """

        transposed_aics_image = aicsimageio.transforms.transpose_to_dims(
            aics_image_numpy_array, source_dims, target_dims
        )
        bit_depth = aics_image_numpy_array.dtype
        max_value_original_depth = np.iinfo(bit_depth).max
        max_value_8_bit = 255

        new_C_squashed_image = np.sum(transposed_aics_image, axis=0)
        # new_C_squashed_image = skimage.color.gray2rgb(new_C_squashed_image, channel_axis=0)
        new_C_squashed_image = np.expand_dims(new_C_squashed_image, 0)
        log.info("Fused channels shape: " + str(np.shape(new_C_squashed_image)))

        retransposed_transposed_aics_image = aicsimageio.transforms.transpose_to_dims(
            new_C_squashed_image, target_dims, source_dims
        )
        log.info(
            "Retransposed Fused channels shape: "
            + str(np.shape(retransposed_transposed_aics_image))
        )
        return (
            retransposed_transposed_aics_image
            * (max_value_8_bit / max_value_original_depth)
        ).astype(np.uint8)

    def make_Z_project(
        self, aics_image_numpy_array, source_dims, target_dims, method_name="max"
    ):
        def select_method(transposed_aics_image, method_name):
            if method_name == "max":
                return np.max(transposed_aics_image, axis=0)
            if method_name == "min":
                return np.min(transposed_aics_image, axis=0)
            if method_name == "sum":
                return np.sum(transposed_aics_image, axis=0)
            if method_name == "average":
                return np.mean(transposed_aics_image, axis=0)
            if method_name == "median":
                return np.median(transposed_aics_image, axis=0)
            if method_name == "sd":
                return np.std(transposed_aics_image, axis=0)
            msg = "invalid value for argument `method_name`"
            raise ValueError(msg)

        transposed_aics_image_array = aicsimageio.transforms.transpose_to_dims(
            aics_image_numpy_array, source_dims, target_dims
        )
        log.info(
            "Transposed_aics_image_array before Z-project: "
            + str(np.shape(transposed_aics_image_array))
        )
        # digit_type = dtype_map[bit_depth]

        z_projected_channel_transposed_image_array = select_method(
            transposed_aics_image_array, method_name
        )
        z_projected_channel_transposed_image_array = np.expand_dims(
            z_projected_channel_transposed_image_array, 0
        )
        log.info(
            "Z_project shape: "
            + str(np.shape(z_projected_channel_transposed_image_array))
        )
        return aicsimageio.transforms.transpose_to_dims(
            z_projected_channel_transposed_image_array, target_dims, source_dims
        )

    def resize_image(self, aics_image, new_width, new_height):
        number_of_timeframes = aics_image.shape[0]
        number_of_channels = aics_image.shape[1]
        z_depth_by_channel = aics_image.shape[2]
        return skimage.transform.resize(
            aics_image,
            (
                number_of_timeframes,
                number_of_channels,
                z_depth_by_channel,
                new_height,
                new_width,
            ),
            order=1,
            mode="reflect",
            cval=0,
            clip=True,
            preserve_range=True,
            anti_aliasing=None,
            anti_aliasing_sigma=None,
        )

    def vignette_pipeline(self):
        image_file_path = self.image_path
        aics_image = AICSImage(image_file_path)
        z_project_method_name = "max"
        thumbnail_height = 256
        thumbnail_width = 256
        (
            source_dims,
            target_dims_for_zprojection,
            target_dims_for_channel_fusion,
        ) = self.get_formalism(aics_image)
        aics_image_numpy_array = aics_image.data
        array_image_1 = self.make_Z_project(
            aics_image_numpy_array,
            source_dims,
            target_dims_for_zprojection,
            z_project_method_name,
        )
        array_image_2 = self.make_fused_channels(
            array_image_1, source_dims, target_dims_for_channel_fusion
        )
        return self.resize_image(array_image_2, thumbnail_height, thumbnail_width)

    def set_vignettes_path(self):
        if not self.image_path.exists():
            msg = f"{self.image_path} not found"
            raise ValueError(msg)
        log.info("Image path: " + str(self.image_path))
        # image_directory = self.image_path.parents[0]
        investigation_directory = self.image_path.parents[2]
        study_name = str(self.image_path.parents[1]).rsplit("/", maxsplit=1)[-1]
        assay_name = str(self.image_path.parents[0]).rsplit("/", maxsplit=1)[-1]
        vignettes_directory = (
            investigation_directory / "ro-crate-preview_files" / study_name / assay_name
        )
        log.info("Vignettes directory: " + str(vignettes_directory))
        Path(vignettes_directory).mkdir(parents=True, exist_ok=True)
        return vignettes_directory

    def set_current_vignette_name_stub(self):
        vignettes_path = self.set_vignettes_path()
        image_name = Path(self.image_path).parts[-1]
        return str(vignettes_path) + "/" + str(image_name) + "_vignette"

    def save_image_as_gif(self):
        numpy_array = self.vignette_numpy_array
        # squeeze Z and C axes (1 and 2) because they are reduced to 1
        np_squeezed = np.squeeze(numpy_array.astype(np.uint8), axis=(1, 2))
        imageio.mimwrite(str(self.vignette_path), np_squeezed)
        # TimeseriesWriter.save(np_squeezed, vignette_path, "TYXS")

    def save_image_as_mp4_ffmpeg(
        self, framerate=60, vcodec="libx264"
    ):  # https://github.com/kkroening/ffmpeg-python/issues/246
        vignette_stub = self.set_current_vignette_name_stub()
        numpy_array = self.vignette_numpy_array
        number, height, width, channels = numpy_array.shape
        process = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="rgb24",
                s=f"{width}x{height}",
            )
            .output(vignette_stub, pix_fmt="yuv420p", vcodec=vcodec, r=framerate)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
        for frame in numpy_array:
            process.stdin.write(frame.astype(np.uint8).tobytes())
        process.stdin.close()
        # process.wait()
