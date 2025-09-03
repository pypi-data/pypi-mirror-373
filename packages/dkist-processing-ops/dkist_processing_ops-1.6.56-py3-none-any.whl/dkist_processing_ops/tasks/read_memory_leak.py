import gc
import logging
from abc import ABC
from pathlib import Path

import numpy as np
from astropy.io import fits
from dkist_processing_common.codecs.fits import fits_hdu_decoder
from dkist_processing_common.codecs.path import path_decoder
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import WorkflowTaskBase


def fits_bytes_decoder(path: Path) -> bytes:
    with open(path, "rb") as f:
        return f.read()


class FitsDataRead(WorkflowTaskBase, ABC):
    @property
    def run_type(self):
        return self.metadata_store_recipe_run_configuration().get("run_type", "file_read")

    def run(self) -> None:
        if self.run_type == "bytes_read":
            bytes_objects = self.read(tags=[Tag.input(), Tag.frame()], decoder=fits_bytes_decoder)
            for i, byte_object in enumerate(bytes_objects):
                pass

        if self.run_type == "bytes_task":
            filepaths = self.read(tags=[Tag.input(), Tag.frame()], decoder=path_decoder)
            for filepath in filepaths:
                with open(filepath, "rb") as f:
                    byte_object = f.read()

        if self.run_type == "file_read":
            hdus = self.read(tags=[Tag.input(), Tag.frame()], decoder=fits_hdu_decoder)
            for hdu in hdus:
                h = hdu.header
                d = hdu.data

        if self.run_type == "file_task":
            filepaths = self.read(tags=[Tag.input(), Tag.frame()], decoder=path_decoder)
            for filepath in filepaths:
                hdu = fits.open(filepath)[1]
                h = hdu.header
                d = hdu.data
