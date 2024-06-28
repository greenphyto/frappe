# Copyright (c) 2023, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe, json
from frappe.model.document import Document
from frappe.utils import now, cstr, cint
from six import string_types


class SyncLog(Document):
	@frappe.whitelist()
	def sync_again(self):
		if not self.method:
			frappe.msgprint("Not have settings")

		settings = frappe.get_hooks("sync_log_method") or {}
		self.method = cint(self.method)
		if self.method in settings:
			func_path = settings[self.method][0]
			frappe.get_attr(func_path)(self)

def create_log(doctype, docname, update_type="Update", method=""):
	# when other doctype is created or edited
	# it will create a pending log
	log = frappe.db.exists("Sync Log", {
		"doc_type": doctype, 
		"docname": docname,
		"status": "Pending",
		"method_id":method
	})

	if not log:
		doc = frappe.new_doc("Sync Log", log)
		doc.doc_type = doctype
		doc.docname = docname
		doc.status = 'Pending'
		doc.update_type = update_type
		doc.method = method
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
		log = frappe.get_doc("Sync Log", log_name)
		log.status = status
		log.sync_on = now()
		log.error = ""
		log.request = ""
		log.status_code = 200
		log.flags.ignore_permissions = 1
		log.save()

	return True

def update_error(logs):
	# logs = [{"log":"log name", "error": "error", "status_code":status_code, "request":"detail request like host, url, method"}]
	if isinstance(logs, string_types):
		logs = json.loads(logs)
	if not isinstance(logs, list):
		logs = [logs]

	for d in logs:
		d = frappe._dict(d)
		log = frappe.get_doc("Sync Log", d.log)
		log.status = "Error"
		log.request = json.dumps(d.request)
		log.error = d.error
		log.sync_on = now()
		log.status_code = d.status_code
		log.flags.ignore_permissions = 1
		log.save()

@frappe.whitelist()
def get_pending_log(filters):
	if isinstance(filters, string_types):
		filters = json.loads(filters)

	if "doctype" in filters:
		cdt = cstr(filters.get("doctype"))
		del filters['doctype']
		filters["doc_type"] = cdt

	base_filters = {"status":['in', ["Pending", "Error"]]}
	base_filters.update(filters)

	logs = frappe.db.get_all("Sync Log", base_filters, [
		'doc_type as doctype', 
		'docname',
		'name',
		'update_type'
	])
	return logs
		