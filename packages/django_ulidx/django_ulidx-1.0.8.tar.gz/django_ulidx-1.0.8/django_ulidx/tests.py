from django import forms
from django.core.exceptions import ValidationError
from django.db import models, connection
from django.db.models import Model
from django.test import TestCase, override_settings

from django_ulidx.models import ULID, ULIDField


class TestModel(Model):
	ulid = ULIDField(primary_key=True)
	name = models.CharField(max_length=100)

	class Meta:
		app_label = "django_ulidx"


class ULIDFieldTests:
	"""Base test class for ULIDField that will be inherited by database-specific test classes"""

	def setUp(self):
		self.model = TestModel
		self.field = self.model._meta.get_field("ulid")

	def test_field_creation(self):
		"""Test that the field is created with correct attributes"""
		self.assertEqual(self.field.max_length, 16)
		self.assertFalse(self.field.editable)
		self.assertEqual(self.field.default, ULID)
		self.assertEqual(self.field.get_internal_type(), "BinaryField")

	def test_db_type(self):
		"""Test that the correct database type is returned for each backend"""
		if connection.vendor == "mysql":
			self.assertEqual(self.field.db_type(connection), "BINARY(16)")
		elif connection.vendor == "sqlite":
			self.assertEqual(self.field.db_type(connection), "BLOB")
		else:  # postgresql
			self.assertEqual(self.field.db_type(connection), "bytea")

	def test_value_conversion(self):
		"""Test conversion between different value types"""
		# Test string to ULID
		ulid_str = "01HGD7XGQZ8K4QZ8K4QZ8K4QZ8"
		ulid_obj = self.field.to_python(ulid_str)
		self.assertIsInstance(ulid_obj, ULID)
		self.assertEqual(str(ulid_obj), ulid_str)

		# Test bytes to ULID
		ulid_bytes = ulid_obj.bytes
		ulid_from_bytes = self.field.to_python(ulid_bytes)
		self.assertIsInstance(ulid_from_bytes, ULID)
		self.assertEqual(ulid_from_bytes, ulid_obj)

		# Test None to ULID
		ulid_none = self.field.to_python(None)
		self.assertIsInstance(ulid_none, ULID)
		self.assertEqual(ulid_none, ULID.from_int(0))

	def test_model_operations(self):
		"""Test model operations with ULIDField"""
		# Create
		ulid_obj = ULID()
		instance = self.model.objects.create(ulid=ulid_obj, name="test")
		self.assertEqual(instance.ulid, ulid_obj)

		# Read
		retrieved = self.model.objects.get(pk=ulid_obj)
		self.assertEqual(retrieved.ulid, ulid_obj)
		self.assertEqual(retrieved.name, "test")

		# Update
		new_name = "updated"
		retrieved.name = new_name
		retrieved.save()
		updated = self.model.objects.get(pk=ulid_obj)
		self.assertEqual(updated.name, new_name)

		# Delete
		retrieved.delete()
		with self.assertRaises(self.model.DoesNotExist):
			self.model.objects.get(pk=ulid_obj)

	def test_form_field(self):
		"""Test form field behavior"""
		form_field = self.field.formfield()
		self.assertIsInstance(form_field, forms.CharField)
		self.assertEqual(form_field.max_length, 26)

		# Test form validation
		ulid_str = "01HGD7XGQZ8K4QZ8K4QZ8K4QZ8"
		self.assertEqual(form_field.clean(ulid_str), ulid_str)

		with self.assertRaises(ValidationError):
			form_field.clean("invalid-ulid")

	def test_migration_serialization(self):
		"""Test that ULID values are properly serialized for migrations"""
		from django.db.migrations.serializer import MigrationWriter
		ulid_obj = ULID()
		serialized = MigrationWriter.serialize(ulid_obj)
		self.assertEqual(serialized[0], "ULID()")
		self.assertEqual(serialized[1], {})


@override_settings(DATABASES={
	"default": {
		"ENGINE": "django.db.backends.sqlite3",
		"NAME": ":memory:",
	}
})
class SQLiteULIDFieldTests(ULIDFieldTests, TestCase):
	"""Test ULIDField with SQLite database"""


@override_settings(DATABASES={
	"default": {
		"ENGINE": "django.db.backends.postgresql",
		"NAME": "django_ulidx",
		"USER": "postgres",
		"PASSWORD": "password",
		"HOST": "postgres",
		"PORT": "5432",
	}
})
class PostgreSQLULIDFieldTests(ULIDFieldTests, TestCase):
	"""Test ULIDField with PostgreSQL database"""


@override_settings(DATABASES={
	"default": {
		"ENGINE": "django.db.backends.mysql",
		"NAME": "django_ulidx",
		"USER": "root",
		"PASSWORD": "password",
		"HOST": "mariadb",
		"PORT": "3306",
	}
})
class MySQLULIDFieldTests(ULIDFieldTests, TestCase):
	"""Test ULIDField with MySQL database"""
