from dataclasses import dataclass
from math import isclose
from pathlib import Path
from typing import Dict, Optional, Type

from threedi_schema import models

from threedi_modelchecker.interfaces import GDALRasterInterface, RasterInterface

from .base import BaseCheck

# interface_cls.is_valid_geotiff returns False if the dataset is empty
# (such as when the column doesn't reference a file) or the dataset is not a valid geotiff.
# It's used on every raster check which reads the raster file in any way,
# to prevent any other code in the check from executing on a bad file.
# On such datasets, RasterExistsCheck and/or RasterIsValidCheck will be raised.


class Context:
    pass


@dataclass
class ServerContext(Context):
    available_rasters: Dict[str, str]
    raster_interface: Type[RasterInterface] = GDALRasterInterface
    epsg_ref_code: int = None
    epsg_ref_name: str = ""


@dataclass
class LocalContext(Context):
    base_path: Path
    raster_interface: Type[RasterInterface] = GDALRasterInterface
    epsg_ref_code: int = None
    epsg_ref_name: str = ""


class BaseRasterCheck(BaseCheck):
    """Baseclass for all raster checks.

    Because these checks are different on local and server systems, subclasses may
    implement 2 methods: is_valid_local and/or is_valid_local.
    """

    def to_check(self, session):
        return (
            super()
            .to_check(session)
            .filter(
                self.column != None,
                self.column != "",
            )
        )

    def get_invalid(self, session):
        context = session.model_checker_context
        raster_interface = context.raster_interface
        if not raster_interface.available():
            return []
        if isinstance(context, ServerContext):
            # max 1 record; we can only have 1 raster per type on the server
            records = list(self.to_check(session).limit(1).all())
            paths = [self.get_path_server(x, context) for x in records]
        else:
            records = list(self.to_check(session).all())
            paths = [self.get_path_local(x, context) for x in records]
        return [
            record
            for (record, path) in zip(records, paths)
            if path is not None and not self.is_valid(path, raster_interface)
        ]

    def get_path_local(self, record, context: LocalContext) -> Optional[str]:
        abs_path = context.base_path.joinpath(
            "rasters", getattr(record, self.column.name)
        )
        if abs_path.exists():
            return str(abs_path)

    def get_path_server(self, record, context: ServerContext) -> str:
        if isinstance(context.available_rasters, dict):
            return context.available_rasters.get(self.column.name)

    def is_valid(self, path: str, interface_cls: Type[RasterInterface]):
        return True


class RasterExistsCheck(BaseRasterCheck):
    """Check whether a file referenced in given Column exists.

    In order to perform this check, the SQLAlchemy session requires a
    `model_checker_context` attribute, which is set automatically by the
    ThreediModelChecker and contains either a LocalContext or
    ServerContextinstance.
    """

    def get_invalid(self, session):
        context = session.model_checker_context
        if isinstance(context, ServerContext):
            # map names of raster files fields in the schema to those in the RasterOptions class
            raster_name_mapping = {
                "friction_coefficient_file": "frict_coef_file",
                "initial_water_level_file": "initial_waterlevel_file",
                "groundwater_hydraulic_conductivity_file": "groundwater_hydro_connectivity_file",
                "max_infiltration_volume_file": "max_infiltration_capacity_file",
            }
            raster_col = self.column.name
            if self.column.name in raster_name_mapping:
                raster_col = raster_name_mapping[self.column.name]
            if raster_col in context.available_rasters:
                return []
            else:
                return self.to_check(session).all()
        else:
            records = list(self.to_check(session).all())
            paths = [self.get_path_local(x, context) for x in records]
            return [record for (record, path) in zip(records, paths) if path is None]

    def description(self):
        return f"The file in {self.column_name} is not present"


class RasterIsValidCheck(BaseRasterCheck):
    """Check whether a file is a geotiff."""

    def is_valid(self, path: str, interface_cls: Type[RasterInterface]):
        with interface_cls(path) as raster:
            return raster.is_valid_geotiff

    def description(self):
        return f"The file in {self.column_name} is not a valid GeoTIFF file"


class RasterHasOneBandCheck(BaseRasterCheck):
    """Check whether a raster has a single band."""

    def is_valid(self, path: str, interface_cls: Type[RasterInterface]):
        with interface_cls(path) as raster:
            if not raster.is_valid_geotiff:
                return True
            return raster.band_count == 1

    def description(self):
        return f"The file in {self.column_name} has multiple or no bands."


class RasterHasMatchingEPSGCheck(BaseRasterCheck):
    """Check whether a raster's EPSG code matches the EPSG code in the global settings for the SQLite."""

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.epsg_ref_name = ""
        self.epsg_ref_code = None

    def get_invalid(self, session):
        if session.model_checker_context.epsg_ref_code is None:
            return []
        self.epsg_ref_name = session.model_checker_context.epsg_ref_name
        self.epsg_ref_code = session.model_checker_context.epsg_ref_code
        return super().get_invalid(session)

    def is_valid(self, path: str, interface_cls: Type[RasterInterface]):
        if self.epsg_ref_code is None:
            return True
        with interface_cls(path) as raster:
            if not raster.is_valid_geotiff or not raster.has_projection:
                return True
            if raster.epsg_code is None:
                return False
            return raster.epsg_code == self.epsg_ref_code

    def description(self):
        return f"The file in {self.column_name} has no EPSG code or the EPSG code does not match does not match {self.epsg_ref_name}"


class RasterSquareCellsCheck(BaseRasterCheck):
    """Check whether a raster has square cells (pixels)"""

    def __init__(self, *args, decimals=7, **kwargs):
        super().__init__(*args, **kwargs)
        self.decimals = decimals

    def is_valid(self, path: str, interface_cls: Type[RasterInterface]):
        with interface_cls(path) as raster:
            if not raster.is_valid_geotiff:
                return True
            dx, dy = raster.pixel_size
            return dx is not None and round(dx, self.decimals) == round(
                dy, self.decimals
            )

    def description(self):
        return f"The raster in {self.column_name} has non-square raster cells."


class RasterGridSizeCheck(BaseRasterCheck):
    """Check whether the global settings' grid size is an even multiple of a raster's cell size (at least 2x)."""

    def get_invalid(self, session):
        minimum_cell_size_query = session.query(
            models.ModelSettings.minimum_cell_size
        ).first()
        if minimum_cell_size_query is not None:
            self.minimum_cell_size = minimum_cell_size_query[0]
        else:
            return []
        return super().get_invalid(session)

    def is_valid(self, path: str, interface_cls: Type[RasterInterface]):
        with interface_cls(path) as raster:
            if not raster.is_valid_geotiff:
                return True
            # the x pixel size is used here,but it is equal to the y pixel size
            try:
                return (
                    isclose(
                        a=((self.minimum_cell_size / raster.pixel_size[0]) % 2),
                        b=0,
                        rel_tol=1e-09,
                    )
                ) and (self.minimum_cell_size >= (2 * raster.pixel_size[0]))
            # if one of the fields is a NoneType it will be caught elsewhere
            except TypeError:
                return True

    def description(self):
        return "model_settings.minimum_cell_size is not a positive even multiple of the raster cell size."


class RasterPixelCountCheck(BaseRasterCheck):
    """Check if the grid does not contain more than a given amount of pixels, default 5 billion"""

    def __init__(self, *args, max_pixels=5e9, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pixels = max_pixels

    def is_valid(self, path: str, interface_cls: Type[RasterInterface]):
        with interface_cls(path) as raster:
            width, height = raster.shape
            return True if width * height <= self.max_pixels else False

    def description(self):
        return f"The file in {self.column_name} exceeds {self.max_pixels} pixels."


class RasterRangeCheck(BaseRasterCheck):
    """Check whether a raster has values outside of provided range.

    Also fails when there are no values in the raster.
    """

    def __init__(
        self,
        min_value=None,
        max_value=None,
        left_inclusive=True,
        right_inclusive=True,
        message=None,
        *args,
        **kwargs,
    ):
        if min_value is None and max_value is None:
            raise ValueError("Please supply at least one of {min_value, max_value}.")
        self.min_value = min_value
        self.max_value = max_value
        self.left_inclusive = left_inclusive
        self.right_inclusive = right_inclusive
        self.message = message
        super().__init__(*args, **kwargs)

    def is_valid(self, path: str, interface_cls: Type[RasterInterface]):
        with interface_cls(path) as raster:
            if not raster.is_valid_geotiff:
                return True
            try:
                raster_min, raster_max = raster.min_max
            except RasterInterface.NoData:
                return False  # no data in the raster is invalid too

        if raster_min is None or raster_max is None:
            return False
        if self.min_value is not None:
            if self.left_inclusive and raster_min < self.min_value:
                return False
            if not self.left_inclusive and raster_min <= self.min_value:
                return False
        if self.max_value is not None:
            if self.right_inclusive and raster_max > self.max_value:
                return False
            if not self.right_inclusive and raster_max >= self.max_value:
                return False

        return True

    def description(self):
        if self.message:
            return self.message
        parts = []
        if self.min_value is not None:
            parts.append(f"{'<' if self.left_inclusive else '<='}{self.min_value}")
        if self.max_value is not None:
            parts.append(f"{'>' if self.right_inclusive else '>='}{self.max_value}")
        return f"{self.column_name} has values {' and/or '.join(parts)} or is empty"


class RasterCompressionUsedCheck(BaseRasterCheck):
    """Checks whether compression was used for the raster"""

    def is_valid(self, path: str, interface_cls: Type[RasterInterface]):
        with interface_cls(path) as raster:
            if not raster.is_valid_geotiff:
                return True
            return raster.compression != "NONE"

    def description(self):
        return f"Raster {self.column_name} is not compressed. It is recommended to use DEFLATE compression. This speeds up uploading and downloading and reduces storage space."


@dataclass
class GDALUnavailable:
    id: int


class GDALAvailableCheck(BaseRasterCheck):
    """Checks whether GDAL is available"""

    def get_invalid(self, session):
        context = session.model_checker_context
        raster_interface = context.raster_interface
        if not raster_interface.available():
            return [GDALUnavailable(id=1)]
        else:
            return []

    def description(self) -> str:
        return "raster checks require GDAL to be available"
