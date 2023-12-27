# Copyright (c) 2023, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

class SyncLog(Document):
	pass

def create_log(doctype, docname):
	# when other doctype is created or edited
	# it will create a pending log
	log = frappe.db.exists("Sync Log", {
		"doc_type": doctype, 
		"docname": docname})

	if not log:
		doc = frappe.new_doc("Sync Log", log)
		doc.doc_type = doctype
		doc.docname = docname
		doc.status = 'Pending'
		doc.insert(ignore_permissions=1)

def delete_log(doctype, docname):
	log = frappe.db.exists("Sync Log", {
		"doc_type": doctype, 
		"docname": docname})

	if log:
		frappe.delete_doc("Sync Log", log)

@frappe.whitelist()
def update_success(log_name, status="Success"):
	frappe.db.set_value("Sync Log", log_name, "status", status)
	frappe.db.set_value("Sync Log", log_name, "sync_on", now())

@frappe.whitelist()
def get_pending_log():
	logs = frappe.db.get_all("Sync Log", {"status":"Pending"}, [
		'doc_type as doctype', 
		'docname as name',
		'name as log_name'
	])
	return logs
		