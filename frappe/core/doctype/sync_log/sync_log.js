// Copyright (c) 2023, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sync Log', {
	print_to_console: function(frm) {
		console.log("REQUEST:",JSON.parse(frm.doc.request));
		console.log("ERROR:",JSON.parse(frm.doc.error));
		frappe.show_alert("View in Browser's console",3);
	},
	refresh: function(frm){
		$(".btn-sync-again").remove();
		if (frm.doc.method){
			frm.page.add_button("Sync Now", ()=>{
				frappe.call({
					method:"sync",
					doc:frm.doc,
					callback: function(){
						frappe.show_alert("Done",2);
						frm.reload_doc();
					}
				})
			}, {btn_class:"btn-sync-again"})
		}
	}
});
