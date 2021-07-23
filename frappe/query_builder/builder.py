from pypika import MySQLQuery, Order, PostgreSQLQuery, Query
from pypika import functions as fn
from pypika import terms
from pypika.queries import Schema, Table
import frappe.query_builder.functions as SpecialFuncs


def get_query_builder(db_type: str) -> Query:
	"""[return the query builder object]

	Args:
			db_type (str): [string value of the db used]

	Returns:
			Query: [Query object]
	"""
	if not db_type:
		db_type = "mariadb"
	selecter = {"mariadb": MariaDB, "postgres": Postgres}
	return selecter[db_type]


class common:
	fn = fn
	terms = terms
	desc = Order.desc
	Schema = Schema

	@staticmethod
	def Table(classname: str, *args, **kwargs) -> Table:
		if not classname.startswith("__"):
			classname = f"tab{classname}"
		return Table(classname, *args, **kwargs)


class MariaDB(common, MySQLQuery):
	Field = terms.Field
	GROUP_CONCAT = SpecialFuncs.GROUP_CONCAT
	Match = SpecialFuncs.Match

	@classmethod
	def from_(cls, class_name, *args, **kwargs):
		if isinstance(class_name, str):
			class_name = f"tab{class_name}"
		return super().from_(class_name, *args, **kwargs)


class Postgres(common, PostgreSQLQuery):
	postgres_field = {"table_name": "relname", "table_rows": "n_tup_ins"}
	information_schema_translation = {"tables": "pg_stat_all_tables"}
	GROUP_CONCAT = SpecialFuncs.STRING_AGG
	Match = SpecialFuncs.TO_TSVECTOR

	@classmethod
	def Field(cls, fieldName, *args, **kwargs):
		if fieldName in cls.postgres_field:
			fieldName = cls.postgres_field[fieldName]
		return terms.Field(fieldName, *args, **kwargs)

	@classmethod
	def from_(cls, class_name, *args, **kwargs):
		if isinstance(class_name, Table):
			if class_name._schema:
				if class_name._schema._name == "information_schema":
					class_name = cls.information_schema_translation[
						class_name._table_name
					]

		elif isinstance(class_name, str):
			class_name = "tab" + class_name

		return super().from_(class_name, *args, **kwargs)
