# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.integrations.firebase import FirebaseNotification
class FirebaseNotificationSettings(Document):
	pass

@frappe.whitelist()
def get_query_test_user(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""
		select distinct user from `tabFirebase User Token`	
	""")

@frappe.whitelist()
def send_message(message, user, title):
	notif = FirebaseNotification()
	return notif.send_message(message, user, title=title)