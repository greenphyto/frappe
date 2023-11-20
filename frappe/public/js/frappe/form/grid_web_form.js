// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

import Grid from "./grid";

export default class GridWeb extends Grid {
	constructor(opts) {
		super(opts)

        console.log("from grid web")
	}

    refresh(){
        super.refresh()

        frappe.web_form.doc[this.df.fieldname] = this.data;
    }
}