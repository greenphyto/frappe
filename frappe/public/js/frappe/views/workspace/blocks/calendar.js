import Block from "./block.js";
export default class Calendar extends Block {
	constructor({ data, config, api, readOnly }) {
		super({ config, api, readOnly });

		this._settings = this.config;
		this._data = this.normalizeData(data);
		this._element = this.getTag();

		this.data = data;
		this.col = this.data.col ? this.data.col : "12";
	}

	normalizeData(data) {
		const newData = {};

		if (typeof data !== "object") {
			data = {};
		}

		newData.calendar_name = data.calendar_name || "";
		newData.col = parseInt(data.col) || 12;

		return newData;
	}

	render() {
		this.wrapper = document.createElement("div");
		if (!this.readOnly) {
			let $widget_head = $(`<div class="widget-head calendar-mode"></div>`);
			let $widget_control = $(`<div class="widget-control"></div>`);

			$widget_head[0].appendChild(this._element);
			$widget_control.appendTo($widget_head);
			$widget_head.appendTo(this.wrapper);

			this.wrapper.classList.add("widget", "calendar", "edit-mode");

			this.add_settings_button();
			this.add_new_block_button();

			frappe.utils.add_custom_button(
				frappe.utils.icon("drag", "xs"),
				null,
				"drag-handle",
				__("Drag"),
				null,
				$widget_control
			);

			$(this._element).find(".calendar-name").show();
			$(this._element).find(".calendar-wrapper").hide();
			return this.wrapper;
		}
		$(this._element).find(".calendar-name").hide();
		$(this._element).find(".calendar-wrapper").show();
		if (!this.calendar_page){
			var wrapper = $(this._element).find(".calendar-wrapper");
			if (frappe.run_calendar){
				this.calendar_page = frappe.run_calendar(wrapper);
			}
		}
		return this._element;
	}

	validate(blockData) {
		return true;
	}

	save() {
		this.wrapper = this._element;
		var element = this.wrapper;
		var calendar_name = $(element).find(".calendar-name").text();
		console.log(71, this.wrapper, calendar_name);

		return {
			calendar_name: calendar_name,
			col: this.get_col(),
		};
	}

	rendered() {
		super.rendered(this._element);
	}

	static get isReadOnlySupported() {
		return true;
	}

	get data() {
		var element = $(this._element)
		this._data.calendar_name = element.find(".calendar-name").text();;

		return this._data;
	}

	set data(data) {
		this._data = this.normalizeData(data);
		if (!this.readOnly && this.wrapper) {
			this.wrapper.classList.add("widget", "header");
		}
	}

	getTag() {
		const tag = document.createElement("DIV");

		let cls = this._data.calendar_name || "calendar-view";
		cls = frappe.scrub(cls);
		tag.innerHTML = `
			<div class='calendar-name'>${cls}</div>
			<div class='calendar-wrapper'></div>
		`;

		tag.classList.add("ce-header");
		tag.classList.add("ce-calendar");
		tag.classList.add(cls);

		if (!this.readOnly) {
			tag.contentEditable = true;
		}

		return tag;
	}

	static get toolbox() {
		return {
			title: "Calendar",
			icon: frappe.utils.icon("table", "sm"),
		};
	}
}

console.log("From calendar")