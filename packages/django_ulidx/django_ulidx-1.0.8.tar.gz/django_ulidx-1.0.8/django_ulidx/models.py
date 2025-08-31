from django.db import models
from django.db.migrations.serializer import BaseSerializer
from django.db.migrations.writer import MigrationWriter
from django.utils.translation import gettext_lazy as _
from ulid import ULID as BaseULID


class ULID(BaseULID):
	pass


class ULIDField(models.Field):
	description = _("Universally Unique Lexicographically Sortable Identifier Field")

	def __init__(self, *args, **kwargs):
		kwargs["max_length"] = 16
		kwargs.setdefault("editable", False)
		kwargs.setdefault("default", ULID)
		super(ULIDField, self).__init__(*args, **kwargs)

	def deconstruct(self):
		name, path, args, kwargs = super().deconstruct()
		del kwargs["max_length"]
		return name, path, args, kwargs

	def db_type(self, connection):
		if connection.vendor == "mysql":
			return "BINARY(16)"
		if connection.vendor == "sqlite":
			return "BLOB"
		return super(ULIDField, self).db_type(connection)

	def get_internal_type(self):
		return "BinaryField"

	def from_db_value(self, value, expression, connection):
		return self.to_python(value)

	def to_python(self, value):
		if isinstance(value, str):
			return ULID.from_str(value)
		elif isinstance(value, bytes):
			return ULID.from_bytes(value)
		elif not value:
			return ULID.from_int(0)
		return value

	def get_prep_value(self, value):
		if isinstance(value, str):
			return bytes(ULID.from_str(value))
		return bytes(value)

	def value_to_string(self, obj):
		value = self.value_from_object(obj)
		if isinstance(value, ULID):
			return str(value)
		elif isinstance(value, bytes):
			return str(ULID.from_bytes(value))
		elif not value:
			return str(ULID.from_int(0))
		return value

	def formfield(self, **kwargs):
		defaults = {'max_length': 26}
		defaults.update(kwargs)
		return super(ULIDField, self).formfield(**defaults)


class UlidSerializer(BaseSerializer):
	def serialize(self):
		return "ULID()", {}


MigrationWriter.register_serializer(ULID, UlidSerializer)
