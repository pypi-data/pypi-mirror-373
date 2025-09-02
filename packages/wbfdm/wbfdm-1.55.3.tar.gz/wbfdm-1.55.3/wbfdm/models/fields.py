import datetime
import decimal
import json
import uuid

from django.db import DEFAULT_DB_ALIAS, models
from django.db.models.sql.where import AND, WhereNode
from django.utils.duration import duration_iso_string
from django.utils.functional import Promise
from django.utils.timezone import is_aware


class CompositeKey(models.AutoField):
    class Key(dict):
        """Dictionary with json-compatible string conversion."""

        def __str__(self):
            return json.dumps(self)

        def __hash__(self):
            return hash(tuple(self[key] for key in sorted(self.keys())))

    def __init__(self, columns: list[str], db_column_ref: str | None = None, *args, **kwargs):
        self.columns = columns
        self.db_column_ref = db_column_ref
        super().__init__(primary_key=True, *args, **kwargs)

    def contribute_to_class(self, cls, name, private_only=False):
        self.set_attributes_from_name(name)
        self.model = cls
        self.concrete = False
        self.editable = False
        if self.db_column_ref:
            self.column = self.db_column_ref
        else:
            self.column = self.model._meta.get_field(self.columns[1]).db_column  # for default order_by
        cls._meta.add_field(self, private=True)  # virtual field
        cls._meta.setup_pk(self)  # acts as pk

        if not getattr(cls, self.attname, None):
            setattr(cls, self.attname, self)

    def get_prep_value(self, value):
        return self.to_python(value)

    def to_python(self, value):
        if value is None or isinstance(value, CompositeKey.Key):
            return value
        if isinstance(value, dict):
            return CompositeKey.Key(value)
        return CompositeKey.Key(json.loads(value))

    def to_json(self, value):
        if isinstance(value, datetime.datetime):
            result = value.isoformat()
            if value.microsecond:
                result = result[:23] + result[26:]
            if result.endswith("+00:00"):
                result = result[:-6] + "Z"
            return result
        elif isinstance(value, datetime.date):
            return value.isoformat()
        elif isinstance(value, datetime.time):
            if is_aware(value):
                raise ValueError("JSON can't represent timezone-aware times.")
            result = value.isoformat()
            if value.microsecond:
                result = result[:12]
            return result
        elif isinstance(value, datetime.timedelta):
            return duration_iso_string(value)
        elif isinstance(value, (decimal.Decimal, uuid.UUID, Promise)):
            return str(value)
        return value

    def bulk_related_objects(self, objs, using=DEFAULT_DB_ALIAS):
        return []

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        return CompositeKey.Key(
            {
                column: self.to_json(self.model._meta.get_field(column).value_from_object(instance))
                for column in self.columns
            }
        )

    def __set__(self, instance, value):
        """
        I hope it's safe to ignore!
        """
        pass


@CompositeKey.register_lookup
class Exact(models.Lookup):
    lookup_name = "exact"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def as_sql(self, compiler, connection):
        fields = [self.lhs.field.model._meta.get_field(column) for column in self.lhs.field.columns]

        lookup_classes = [field.get_lookup("exact") for field in fields]

        lookups = [
            lookup_class(field.get_col(self.lhs.alias), self.rhs[column])
            for lookup_class, field, column in zip(lookup_classes, fields, self.lhs.field.columns)
        ]

        value_constraint = WhereNode()
        for lookup in lookups:
            value_constraint.add(lookup, AND)
        return value_constraint.as_sql(compiler, connection)
