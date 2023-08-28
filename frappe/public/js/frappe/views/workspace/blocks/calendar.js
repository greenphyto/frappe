import Block from "./block.js";
export default class Calendar extends Block {
	static get toolbox() {
		return {
			title: "Calendar",
			icon: frappe.utils.icon("calendar", "sm"),
		};
	}

	static get isReadOnlySupported() {
		return true;
	}

	constructor({ data, api, config, readOnly }) {
		super({ data, api, config, readOnly });
		this.col = this.data.col ? this.data.col : "12";
		this.allow_customization = !this.readOnly;
		this.options = {
			allow_sorting: this.allow_customization,
			allow_create: this.allow_customization,
			allow_delete: this.allow_customization,
			allow_hiding: false,
			allow_edit: true,
			allow_resize: false,
			min_width: 12,
			max_widget_count: 2,
		};
	}

    render() {
		this.wrapper = document.createElement("div");
		this.wrapper.classList.add("widget", "calendar");
		if (!this.readOnly) {
			let $calendar = $(`
				<div class="widget-head">
					<div class="calendar-left"></div>
					<div>${__("Calendar")}</div>
					<div class="widget-control"></div>
				</div>
			`);
			$calendar.appendTo(this.wrapper);

			this.wrapper.classList.add("edit-mode");
			this.wrapper.style.minHeight = 500 + "px";

			let $widget_control = $calendar.find(".widget-control");

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
		}
		return this.wrapper;
	}

	save() {
		return {
			col: this.get_col(),
		};
	}
}