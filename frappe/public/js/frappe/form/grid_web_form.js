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

    on(field, handler){
        if (!this.events) this.events = {};
        if (!this.events[field] ) this.events[field]=[handler];
        else{
            this.events[field].push(handler); 
        }
    }

    run_events(field, idx, value){
        var table_field = this.df.fieldname;
        if (this.events && this.events[field]){
            $.each(this.events[field], (i, func)=>{
                func(table_field, idx, value);
            })
        }
    }
}