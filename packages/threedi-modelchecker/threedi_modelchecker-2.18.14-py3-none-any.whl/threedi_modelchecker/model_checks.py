from typing import Dict, Iterator, NamedTuple, Optional, Tuple

from threedi_schema import models, ThreediDatabase

from .checks.base import BaseCheck, CheckLevel
from .checks.raster import LocalContext, ServerContext
from .config import Config

__all__ = ["ThreediModelChecker"]


def get_epsg_data_from_raster(session) -> Tuple[int, str]:
    """
    Retrieve epsg code for schematisation loaded in session. This is done by
    iterating over all geometries in the declared models and all raster files, and
    stopping at the first geometry or raster file with data.

    Returns the epsg code and the name (table.column) of the source.
    """
    context = session.model_checker_context
    raster_interface = context.raster_interface if context is not None else None
    epsg_code = None
    epsg_source = ""
    raster = models.ModelSettings.dem_file
    raster_files = session.query(raster).filter(raster != None, raster != "").first()
    if raster_files is not None and raster_files is not None:
        if isinstance(context, ServerContext):
            if isinstance(context.available_rasters, dict):
                abs_path = context.available_rasters.get(raster.name)
        else:
            abs_path = context.base_path.joinpath("rasters", raster_files[0])
        with raster_interface(abs_path) as ro:
            if ro.epsg_code is not None:
                epsg_code = ro.epsg_code
                epsg_source = "model_settings.dem_file"
    return epsg_code, epsg_source


class ThreediModelChecker:
    def __init__(
        self,
        threedi_db: ThreediDatabase,
        context: Optional[Dict] = None,
        allow_beta_features=False,
    ):
        """Initialize the model checker.

        Optionally, supply the context of the model check:

        - "context_type": "local" or "server", default "local"
        - "raster_interface": a threedi_modelchecker.interfaces.RasterInterface subclass
        - "base_path": (only local) path where to look for rasters (defaults to the db's directory)
        - "available_rasters": (only server) a dict of raster_option -> raster url
        """
        self.db = threedi_db
        self.schema = self.db.schema
        self.schema.validate_schema()
        self.config = Config(
            models=self.models, allow_beta_features=allow_beta_features
        )
        context = {} if context is None else context.copy()
        context_type = context.pop("context_type", "local")
        session = self.db.get_session()
        if self.db.schema.epsg_code is not None:
            context["epsg_ref_code"] = self.db.schema.epsg_code
            context["epsg_ref_name"] = self.db.schema.epsg_source
        else:
            epsg_ref_code, epsg_ref_name = get_epsg_data_from_raster(session)
            context["epsg_ref_code"] = epsg_ref_code
            context["epsg_ref_name"] = epsg_ref_name

        if context_type == "local":
            context.setdefault("base_path", self.db.base_path)
            self.context = LocalContext(**context)
        elif context_type == "server":
            self.context = ServerContext(**context)
        else:
            raise ValueError(f"Unknown context_type '{context_type}'")

        session.model_checker_context = self.context

    @property
    def models(self):
        """Returns a list of declared models"""
        return self.schema.declared_models

    def errors(
        self, level=CheckLevel.ERROR, ignore_checks=None
    ) -> Iterator[Tuple[BaseCheck, NamedTuple]]:
        """Iterates and applies checks, returning any failing rows.

        By default, checks of WARNING and INFO level are ignored.

        :return: Tuple of the applied check and the failing row.
        """

        session = self.db.get_session()
        session.model_checker_context = self.context
        for check in self.checks(level=level, ignore_checks=ignore_checks):
            model_errors = check.get_invalid(session)
            for error_row in model_errors:
                yield check, error_row

    def checks(self, level=CheckLevel.ERROR, ignore_checks=None) -> Iterator[BaseCheck]:
        """Iterates over all configured checks

        :return: implementations of BaseChecks
        """
        for check in self.config.iter_checks(level=level, ignore_checks=ignore_checks):
            yield check

    def check_table(self, table):
        pass

    def check_column(self, column):
        pass
