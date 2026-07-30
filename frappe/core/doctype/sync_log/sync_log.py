# Copyright (c) 2023, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe, json
from frappe.model.document import Document
from frappe.utils import now, cstr, cint, flt
from six import string_types


class SyncLog(Document):
	@frappe.whitelist()
	def sync(self, save_log=False):
		if not self.method:
			frappe.msgprint("Not have settings")

		settings = frappe.get_hooks("sync_log_method") or {}
		self.db_set("trial", 0)
		self.method = cint(self.method)
		if save_log:
			self.save_log = 1

		if self.method in settings:
			func_path = settings[self.method][0]
			try:
				frappe.get_attr(func_path)(self)
			except Exception as e:
				tcb = frappe.get_traceback()
				data = {
					"error": cstr(e),
					"traceback":tcb
				} 
				self.db_set("request", json.dumps(func_path))
				self.db_set("status", "Error")
				self.db_set("error", json.dumps(data))

def create_log(doctype, docname, update_type="", method="", doc_method=""):
	# when other doctype is created or edited
	# it will create a pending log

	if not update_type and doc_method in ['on_trash', 'after_delete']:
		update_type = "Delete"

	if not update_type:
		update_type = "Update"

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
		doc.doc_method = doc_method
		doc.insert(ignore_permissions=1)
		return doc.name
	
	elif update_type in ('Delete', 'Cancel'):
		frappe.db.set_value("Sync Log", log, "update_type", update_type)

	return log

def delete_log(doctype, docname):
	logs = frappe.db.get_list("Sync Log", {"docname":docname}, ['name', 'doc_method', 'status'])
	
	valid = True
	if logs:
		for d in logs:
			if d.status == "Pending":
				frappe.delete_doc("Sync Log", d.name)
			else:
				valid = False

	return valid

@frappe.whitelist()
def update_success(logs, status="Success"):
	if isinstance(logs, string_types):
		logs = json.loads(logs)
	if not isinstance(logs, list):
		logs = [logs]

	for d in logs:
		d = frappe._dict(d)
		log_name = d.log
		if not isinstance(log_name, string_types):
			log_name = log_name.get("name")
		log = frappe.get_doc("Sync Log", log_name)
		log.status = status
		log.sync_on = now()
		log.error = ""
		if d.save_log or frappe.local.conf.testing_site:
			log.request = json.dumps(d.request)
			log.save_log = d.save_log
		log.status_code = d.status_code
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
		trial = cint(log.get("trial")) + 1
		if trial > 3:
			log.status = "Expired"
		else:
			log.trial = trial
		log.flags.ignore_permissions = 1
		log.save()

@frappe.whitelist()
def get_pending_log(filters, unique=False):
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
	], order_by="creation desc")

	if unique:
		unique_data = []
		new_log = []
		for d in logs:
			if d.name not in unique_data:
				unique_data.append(d.name)
				new_log.append(d)
		
		return new_log

	return logs
	
def nonactive_older_logs(doctype, docname):
	# set expired for same log for doctype and docname, just left over for newest log
	logs = frappe.db.sql(""" select distinct docname, doc_type, creation from `tabSync Log` where status = "Pending" and doc_type = %s  order by creation desc """, (doctype), as_dict=1)
	unique_data = []
	for d in logs:
		if d.name not in unique_data:
			unique_data.append(d.name)
	
	frappe.db.sql("update `tabSync Log` set status = 'Expired' where name not in %(name_list)s and doctype %(doctype)s and docname %(docname)s ", {
		'name_list':unique_data,
		'doctype':doctype,
		'docname':docname
	})


