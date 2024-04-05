# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FirebaseUserToken(Document):
	pass


@frappe.whitelist()
def create_firebase_token(token, user="", type='Android'):
	user = user or frappe.session.user
	exist_user = frappe.db.get_value("Firebase User Token", {"token":"token"}, ['name',"user"], as_dict=1)
	if exist_user:
		if exist_user.user != user:
			frappe.db.set_value("Firebase User Token", exist_user.name, "user", user)
	else:
		log = frappe.new_doc("Firebase User Token")
		log.user = user
		log.type = type
		log.token = token
		log.insert()
	
	return True

@frappe.whitelist()
def delete_firebase_token(token="", user="", type='Android'):
	user = user or frappe.session.user
	exist_user = None
	if token:
		exist_user = frappe.db.get_value("Firebase User Token", {"token": token})

	if not exist_user:
		exist_user = frappe.db.get_value("Firebase User Token", {"user": user, 'type':type})
	
	if exist_user:
		frappe.delete_doc("Firebase User Token", exist_user,ignore_permissions=1)
	
	frappe.db.commit()

	return True