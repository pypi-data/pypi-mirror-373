from abc import ABC, abstractmethod
from enum import IntEnum
from typing import List, NamedTuple

from geoalchemy2.functions import ST_SRID
from sqlalchemy import and_, false, func, types
from sqlalchemy.orm.session import Session
from threedi_schema.domain import custom_types


class CheckLevel(IntEnum):
    ERROR = 40
    FUTURE_ERROR = 39
    WARNING = 30
    INFO = 20

    @classmethod
    def get(cls, value):
        """Get a CheckLevel from a CheckLevel, str or int."""
        if isinstance(value, cls):
            return value
        elif isinstance(value, str):
            return cls[value.upper()]
        else:
            return cls(value)


class BaseCheck(ABC):
    """Base class for all checks.

    A Check defines a constraint on a specific column and its table.
    One can validate if the constrain holds using the method `get_invalid()`.
    This method will return a list of rows (as named_tuples) which are invalid.
    """

    def __init__(
        self,
        column,
        filters=None,
        level=CheckLevel.ERROR,
        error_code=0,
        is_beta_check=False,
    ):
        self.column = column
        self.table = column.table
        self.filters = filters
        self.error_code = int(error_code)
        self.level = CheckLevel.get(level)
        self.is_beta_check = is_beta_check

    @abstractmethod
    def get_invalid(self, session: Session) -> List[NamedTuple]:
        """Return a list of rows (named_tuples) which are invalid.

        What is invalid is defined in the check. Returns an empty list if no
        invalid rows are present.

        :param session: sqlalchemy.orm.session.Session
        :return: list of named_tuples or empty list if there are no invalid
            rows
        """
        pass

    def get_valid(self, session: Session) -> List[NamedTuple]:
        """Return a list of rows (named_tuples) which are valid.

        :param session: sqlalchemy.orm.session.Session
        :return: list of named_tuples or empty list if there are no valid rows
        """
        all_rows = self.to_check(session)
        invalid_row_ids = set([row.id for row in self.get_invalid(session)])
        valid = []
        for row in all_rows:
            if row.id not in invalid_row_ids:
                valid.append(row)
        return valid

    def to_check(self, session):
        """Return a Query object filtering on the rows this check is applied.

        :param session: sqlalchemy.orm.session.Session
        :return: sqlalchemy.Query
        """
        query = session.query(self.table)
        if self.filters is not None:
            query = query.filter(self.filters)
        return query

    @property
    def column_name(self) -> str:
        return f"{self.table.name}.{self.column.name}"

    def description(self) -> str:
        """Return a string explaining why rows are invalid according to this
        check.

        :return: string
        """
        return "Invalid value in column '%s'" % self.column_name

    def __repr__(self) -> str:
        return "<%s: %s>" % (self.__class__.__name__, self.column_name)


class QueryCheck(BaseCheck):
    """Specify a sqlalchemy.orm.Query object to return invalid instances"""

    def __init__(
        self,
        column,
        invalid,
        message,
        filters=None,
        level=CheckLevel.ERROR,
        error_code=0,
        is_beta_check=False,
    ):
        super().__init__(
            column, level=level, error_code=error_code, is_beta_check=is_beta_check
        )
        self.invalid = invalid
        self.message = message
        self.filters = filters

    def get_invalid(self, session):
        query = self.invalid.with_session(session)
        if self.filters is not None:
            query = query.filter(self.filters)
        return query.all()

    def description(self):
        return self.message


class ForeignKeyCheck(BaseCheck):
    """Check all values in `column` are in `reference_column`.

    Null values are ignored."""

    def __init__(self, reference_column, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reference_column = reference_column

    def get_invalid(self, session):
        q_invalid = self.to_check(session)
        invalid_foreign_keys_query = q_invalid.filter(
            self.column.notin_(session.query(self.reference_column)),
            self.column != None,
        )
        return invalid_foreign_keys_query.all()

    def description(self):
        return "%s refers to a non-existing %s" % (
            self.column_name,
            self.reference_column.table,
        )


class UniqueCheck(BaseCheck):
    """Check all values in `column` are unique

    Null values are ignored."""

    def __init__(self, columns, message=None, **kwargs):
        if not isinstance(columns, (list, tuple)):
            columns = (columns,)
        self.columns = columns
        self.message = message
        super().__init__(column=columns[0], **kwargs)

    def get_invalid(self, session):
        duplicate_values = (
            session.query(*self.columns)
            .group_by(*self.columns)
            .having(func.count(self.column) > 1)
        ).subquery()
        join_clause = and_(
            *[getattr(duplicate_values.c, c.name) == c for c in self.columns]
        )
        q_invalid = self.to_check(session).join(duplicate_values, join_clause)
        return q_invalid.all()

    def description(self):
        if self.message:
            return self.message
        elif len(self.columns) > 1:
            return f"columns {sorted({c.name for c in self.columns})} in table {self.table.name} should be unique together"
        else:
            return f"{self.column_name} should be unique"


class AllEqualCheck(BaseCheck):
    """Check all values in `column` are the same, including NULL values."""

    def get_invalid(self, session):
        val = session.query(self.column).limit(1).scalar()
        if val is None:
            clause = self.column != None
        else:
            clause = (self.column != val) | (self.column == None)
        return self.to_check(session).filter(clause).all()

    def description(self):
        return f"{self.column_name} is different and is ignored if it is not in the first record"


class NotNullCheck(BaseCheck):
    """ "Check all values in `column` that are not null"""

    def get_invalid(self, session):
        q_invalid = self.to_check(session)
        not_null_query = q_invalid.filter(self.column == None)
        return not_null_query.all()

    def description(self):
        return f"{self.column_name} cannot be null"


class TypeCheck(BaseCheck):
    """Check all values in `column` that are of the column defined type.

    Null values are ignored."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_types = _sqlalchemy_to_sqlite_types(self.column.type)

    def get_invalid(self, session):
        if ("sqlite" not in session.bind.dialect.dialect_description) and (
            "geopackage" not in session.bind.dialect.dialect_description
        ):
            return []
        q_invalid = self.to_check(session)
        invalid_type_query = q_invalid.filter(
            func.typeof(self.column).notin_(self.expected_types),
            func.typeof(self.column) != "null",
        )
        return invalid_type_query.all()

    def description(self):
        return f"{self.column_name} is not of type {self.expected_types}"


def _sqlalchemy_to_sqlite_types(column_type):
    """Convert the sqlalchemy column type to allowed sqlite data types

    Returns the value similar as the sqlite 'typeof' function.
    Raises TypeError if the column type is unknown.
    See https://www.sqlite.org/datatype3.html

    :param column_type: sqlalchemy.column
    :return: (str)
    """
    if isinstance(column_type, types.TypeDecorator):
        column_type = column_type.impl

    if isinstance(column_type, types.String):
        return ["text"]
    elif isinstance(column_type, (types.Float, types.Numeric)):
        return ["integer", "numeric", "real"]
    elif isinstance(column_type, types.Integer):
        return ["integer"]
    elif isinstance(column_type, types.Boolean):
        return ["integer"]
    elif isinstance(column_type, types.Date):
        return ["text"]
    elif isinstance(column_type, custom_types.Geometry):
        return ["blob"]
    elif isinstance(column_type, types.TIMESTAMP):
        return ["text"]
    else:
        raise TypeError("Unknown column type: %s" % column_type)


class GeometryCheck(BaseCheck):
    """Check all values in `column` are a valid geometry.

    Null values are ignored."""

    def get_invalid(self, session):
        q_invalid = self.to_check(session)
        invalid_geometries = q_invalid.filter(
            func.ST_IsValid(self.column) != True, self.column != None
        )
        return invalid_geometries.all()

    def description(self):
        return f"{self.column_name} is an invalid geometry"


class GeometryTypeCheck(BaseCheck):
    """Check all values in `column` are of geometry type in defined in
    `column`.

    Null values are ignored"""

    def get_invalid(self, session):
        expected_geometry_type = _get_geometry_type(
            self.column, dialect=session.bind.dialect.name
        )
        q_invalid = self.to_check(session)
        if expected_geometry_type is None:
            # skip in case of generic GEOMETRY column
            return q_invalid.filter(false())
        invalid_geometry_types_q = q_invalid.filter(
            func.ST_GeometryType(self.column) != expected_geometry_type,
            self.column != None,
        )
        return invalid_geometry_types_q.all()

    def description(self):
        return "%s has invalid geometry type, expected %s" % (
            self.column_name,
            self.column.type.geometry_type,
        )


def _get_geometry_type(column, dialect):
    if column.type.geometry_type == "GEOMETRY":
        return  # should skip the check
    if dialect in ["sqlite", "geopackage"]:
        return column.type.geometry_type
    elif dialect == "postgresql":
        geom_type = column.type.geometry_type.capitalize()
        return "ST_%s" % geom_type
    else:
        raise TypeError("Unexpected dialect %s" % dialect)


class EnumCheck(BaseCheck):
    """Check all values in `column` are within the defined Enum values of
    `column`.

    Unexpected values are values not defined by its enum_class.

    Null values are ignored"""

    def get_invalid(self, session):
        q_invalid = self.to_check(session)
        invalid_values_q = q_invalid.filter(
            self.column.notin_(list(self.column.type.enum_class))
        )
        return invalid_values_q.all()

    def description(self):
        allowed = sorted({x.value for x in self.column.type.enum_class})
        return f"{self.column_name} is not one of {allowed}"


class RangeCheck(BaseCheck):
    """Check to if all values are within range [min_value, max_value]

    Use left_inclusive and right_inclusive to specify whether the min/max values
    themselves should be considered valid. By default they are both considered
    valid.
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

    def get_invalid(self, session):
        conditions = []
        if self.min_value is not None:
            if self.left_inclusive:
                conditions.append(self.column >= self.min_value)
            else:
                conditions.append(self.column > self.min_value)
        if self.max_value is not None:
            if self.right_inclusive:
                conditions.append(self.column <= self.max_value)
            else:
                conditions.append(self.column < self.max_value)
        return self.to_check(session).filter(~and_(*conditions)).all()

    def description(self):
        if self.message:
            return self.message
        parts = []
        if self.min_value is not None:
            parts.append(f"{'<' if self.left_inclusive else '<='}{self.min_value}")
        if self.max_value is not None:
            parts.append(f"{'>' if self.right_inclusive else '>='}{self.max_value}")
        return f"{self.column_name} is {' and/or '.join(parts)}"


class ListOfIntsCheck(BaseCheck):
    def get_invalid(self, session):
        invalids = []
        for record in self.to_check(session).filter(
            (self.column != None) & (self.column != "")
        ):
            # check if casting to int works
            try:
                [int(x) for x in getattr(record, self.column.name).split(",")]
            except ValueError:
                invalids.append(record)
        return invalids

    def description(self) -> str:
        return (
            f"{self.table.name}.{self.column} is not a comma seperated list of integers"
        )


class EPSGGeomCheck(BaseCheck):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.epsg_ref_name = ""

    def get_invalid(self, session: Session) -> List[NamedTuple]:
        self.epsg_ref_name = session.model_checker_context.epsg_ref_name
        if session.model_checker_context.epsg_ref_code is None:
            return []
        return (
            self.to_check(session)
            .filter(ST_SRID(self.column) != session.model_checker_context.epsg_ref_code)
            .all()
        )

    def description(self) -> str:
        return f"The epsg of {self.table.name}.{self.column_name} should match {self.epsg_ref_name}"
