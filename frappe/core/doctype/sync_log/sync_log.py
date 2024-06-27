# Copyright (c) 2023, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe, json
from frappe.model.document import Document
from frappe.utils import now, cstr
from six import string_types


class SyncLog(Document):
	pass

def create_log(doctype, docname, update_type="Update"):
	# when other doctype is created or edited
	# it will create a pending log
	log = frappe.db.exists("Sync Log", {
		"doc_type": doctype, 
		"docname": docname,
		"status": "Pending"
	})

	if not log:
		doc = frappe.new_doc("Sync Log", log)
		doc.doc_type = doctype
		doc.docname = docname
		doc.status = 'Pending'
		doc.update_type = update_type
		doc.insert(ignore_permissions=1)
	elif update_type in ('Delete', 'Cancel'):
		frappe.db.set_value("Sync Log", log, "update_type", update_type)

def delete_log(doctype, docname):
	log = frappe.db.exists("Sync Log", {
		"doc_type": doctype, 
		"docname": docname,
		"status": "Pending"
	})

	if log:
		frappe.delete_doc("Sync Log", log)
		return True
	else:
		return False

@frappe.whitelist()
def update_success(logs, status="Success"):
	if isinstance(logs, string_types):
		logs = json.loads(logs)
	if not isinstance(logs, list):
		logs = [logs]

	for log_name in logs:
		if not isinstance(log_name, string_types):
			log_name = log_name.get("name")
		frappe.db.set_value("Sync Log", log_name, "status", status)
		frappe.db.set_value("Sync Log", log_name, "sync_on", now())

	return True

@frappe.whitelist()
def get_pending_log(filters):
	if isinstance(filters, string_types):
		filters = json.loads(filters)

	if "doctype" in filters:
		cdt = cstr(filters.get("doctype"))
		del filters['doctype']
		filters["doc_type"] = cdt

	base_filters = {"status":"Pending"}
	base_filters.update(filters)

	logs = frappe.db.get_all("Sync Log", base_filters, [
		'doc_type as doctype', 
		'docname',
		'name',
		'update_type'
	])
	return logs
		