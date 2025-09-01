"""
MetroUI components for Django.
"""

from .css import merge_css_classes
from .html import render_tag


def render_alert(content, alert_type="info", dismissible=False, **attrs):
	"""
	Renders MetroUI alert component.

	Args:
		content: Alert content
		alert_type: Alert type (info, success, warning, danger, error)
		dismissible: Whether alert can be dismissed
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": f"alert alert-{alert_type}",
		"role": "alert"
	}

	if dismissible:
		default_attrs["class"] = merge_css_classes(default_attrs["class"], "alert-dismissible")

	# Merge with custom attributes
	final_attrs = {**default_attrs, **attrs}

	if dismissible:
		close_button = render_tag(
			"button",
			{
				"type": "button",
				"class": "button button-mini",
				"data-role": "close",
				"aria-label": "Close"
			},
			"&times;"
		)
		content = f"{content}{close_button}"

	return render_tag("div", attrs=final_attrs, content=content)


def render_button(content, button_type="default", size=None, outline=False, **attrs):
	"""
	Renders MetroUI button component.

	Args:
		content: Button text
		button_type: Button type (default, primary, secondary, success, danger, warning, info)
		size: Button size (sm, lg)
		outline: Outline style
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"type": "button",
		"class": "button"
	}

	if button_type != "default":
		if outline:
			default_attrs["class"] = merge_css_classes(default_attrs["class"], f"outline-{button_type}")
		else:
			default_attrs["class"] = merge_css_classes(default_attrs["class"], button_type)

	if size:
		default_attrs["class"] = merge_css_classes(default_attrs["class"], f"button-{size}")

	# Merge with custom attributes
	final_attrs = {**default_attrs, **attrs}

	return render_tag("button", attrs=final_attrs, content=content)


def render_tile(title, content=None, size="medium", color="blue", icon=None, **attrs):
	"""
	Renders MetroUI tile component.

	Args:
		title: Tile title
		content: Additional content
		size: Tile size (small, medium, large, wide, tall)
		color: Tile color
		icon: MetroUI icon
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": f"tile tile-{size} tile-{color}",
		"data-role": "tile"
	}

	if icon:
		default_attrs["data-icon"] = icon

	# Merge with custom attributes
	final_attrs = {**default_attrs, **attrs}

	tile_content = f"<h3 class='tile-title'>{title}</h3>"

	if content:
		tile_content += f"<small>{content}</small>"

	return render_tag("div", attrs=final_attrs, content=tile_content)


def render_card(header=None, content=None, footer=None, **attrs):
	"""
	Renders MetroUI card component.

	Args:
		header: Card header
		content: Card content
		footer: Card footer
		**attrs: Additional HTML attributes
	"""
	default_attrs = {"class": "card"}

	# Merge with custom attributes
	final_attrs = {**default_attrs, **attrs}

	card_parts = []

	if header:
		card_parts.append(render_tag("div", {"class": "card-header"}, header))

	if content:
		card_parts.append(render_tag("div", {"class": "card-content"}, content))

	if footer:
		card_parts.append(render_tag("div", {"class": "card-footer"}, footer))

	if not card_parts:
		card_parts.append(render_tag("div", {"class": "card-content"}, ""))

	return render_tag("div", attrs=final_attrs, content="".join(card_parts))


def render_progress(value, max_value=100, color="blue", size="default", **attrs):
	"""
	Renders MetroUI progress bar component.

	Args:
		value: Current value
		max_value: Maximum value
		color: Progress bar color
		size: Size (mini, small, large)
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": f"progress progress-{color}",
		"data-role": "progress",
		"data-value": str(value),
		"data-max": str(max_value)
	}

	if size != "default":
		default_attrs["class"] = merge_css_classes(default_attrs["class"], f"progress-{size}")

	# Merge with custom attributes
	final_attrs = {**default_attrs, **attrs}

	return render_tag("div", attrs=final_attrs, content="")


def render_accordion(items, **attrs):
	"""
	Renders MetroUI accordion component.

	Args:
		items: List of dictionaries with 'title' and 'content' keys
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "accordion",
		"data-role": "accordion"
	}

	# Merge with custom attributes
	final_attrs = {**default_attrs, **attrs}

	accordion_items = []
	for i, item in enumerate(items):
		item_html = render_tag(
			"div",
			{"class": "accordion-frame"},
			render_tag("a", {"class": "accordion-title", "href": "#"}, item.get('title', '')) +
			render_tag("div", {"class": "accordion-content"}, item.get('content', ''))
		)
		accordion_items.append(item_html)

	return render_tag("div", attrs=final_attrs, content="".join(accordion_items))


def render_calendar(**attrs):
	"""
	Renders MetroUI calendar component.

	Args:
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "calendar",
		"data-role": "calendar"
	}

	# Merge with custom attributes
	final_attrs = {**default_attrs, **attrs}

	return render_tag("div", attrs=final_attrs, content="")


def render_dialog(title, content, **attrs):
	"""
	Renders MetroUI dialog component.

	Args:
		title: Dialog title
		content: Dialog content
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "dialog",
		"data-role": "dialog"
	}

	# Merge with custom attributes
	final_attrs = {**default_attrs, **attrs}

	dialog_content = render_tag("div", {"class": "dialog-title"}, title) + \
					 render_tag("div", {"class": "dialog-content"}, content)

	return render_tag("div", attrs=final_attrs, content=dialog_content)


def render_dropdown(items, button_text="Dropdown", **attrs):
	"""
	Renders MetroUI dropdown component.

	Args:
		items: List of dropdown items
		button_text: Button text
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "dropdown",
		"data-role": "dropdown"
	}

	# Merge with custom attributes
	final_attrs = {**default_attrs, **attrs}

	button = render_tag("button", {"class": "button dropdown-toggle"}, button_text)

	dropdown_items = []
	for item in items:
		if isinstance(item, dict):
			item_html = render_tag("a", {"href": item.get('url', '#')}, item.get('text', ''))
		else:
			item_html = render_tag("a", {"href": "#"}, str(item))
		dropdown_items.append(render_tag("li", {}, item_html))

	dropdown_menu = render_tag("ul", {"class": "dropdown-menu"}, "".join(dropdown_items))

	return render_tag("div", attrs=final_attrs, content=button + dropdown_menu)


def render_input(input_type="text", placeholder="", **attrs):
	"""
	Renders MetroUI input component.

	Args:
		input_type: Input field type
		placeholder: Placeholder text
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"type": input_type,
		"class": "input",
		"data-role": "input"
	}

	if placeholder:
		default_attrs["placeholder"] = placeholder

	# Merge with custom attributes
	final_attrs = {**default_attrs, **attrs}

	return render_tag("input", attrs=final_attrs, close=False)


def render_list(items, list_type="ul", **attrs):
	"""
	Renders MetroUI list component.

	Args:
		items: List of items
		list_type: List type (ul, ol)
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "list",
		"data-role": "list"
	}

	# Merge with custom attributes
	final_attrs = {**default_attrs, **attrs}

	list_items = []
	for item in items:
		if isinstance(item, dict):
			item_html = render_tag("a", {"href": item.get('url', '#')}, item.get('text', ''))
		else:
			item_html = str(item)
		list_items.append(render_tag("li", {}, item_html))

	return render_tag(list_type, attrs=final_attrs, content="".join(list_items))


def render_menu(items, **attrs):
	"""
	Renders MetroUI menu component.

	Args:
		items: List of menu items
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "menu",
		"data-role": "menu"
	}

	# Merge with custom attributes
	final_attrs = {**default_attrs, **attrs}

	menu_items = []
	for item in items:
		if isinstance(item, dict):
			item_html = render_tag("a", {"href": item.get('url', '#')}, item.get('text', ''))
		else:
			item_html = render_tag("a", {"href": "#"}, str(item))
		menu_items.append(render_tag("li", {}, item_html))

	return render_tag("ul", attrs=final_attrs, content="".join(menu_items))


def render_navigation(items, **attrs):
	"""
	Renders MetroUI navigation component.

	Args:
		items: List of navigation items
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "navigation",
		"data-role": "navigation"
	}

	final_attrs = {**default_attrs, **attrs}

	nav_items = []
	for item in items:
		if isinstance(item, dict):
			item_html = render_tag("a", {"href": item.get('url', '#')}, item.get('text', ''))
		else:
			item_html = render_tag("a", {"href": "#"}, str(item))
		nav_items.append(render_tag("li", {}, item_html))

	return render_tag("nav", attrs=final_attrs, content=render_tag("ul", {}, "".join(nav_items)))


def render_panel(title=None, content=None, **attrs):
	"""
	Renders MetroUI panel component.

	Args:
		title: Panel title
		content: Panel content
		**attrs: Дополнительные HTML атрибуты
	"""
	default_attrs = {"class": "panel"}

	final_attrs = {**default_attrs, **attrs}

	panel_parts = []

	if title:
		panel_parts.append(render_tag("div", {"class": "panel-header"}, title))

	if content:
		panel_parts.append(render_tag("div", {"class": "panel-content"}, content))

	if not panel_parts:
		panel_parts.append(render_tag("div", {"class": "panel-content"}, ""))

	return render_tag("div", attrs=final_attrs, content="".join(panel_parts))


def render_sidebar(items, **attrs):
	"""
	Renders MetroUI sidebar component.

	Args:
		items: List of sidebar items
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "sidebar",
		"data-role": "sidebar"
	}

	final_attrs = {**default_attrs, **attrs}

	sidebar_items = []
	for item in items:
		if isinstance(item, dict):
			item_html = render_tag("a", {"href": item.get('url', '#')}, item.get('text', ''))
		else:
			item_html = render_tag("a", {"href": "#"}, str(item))
		sidebar_items.append(render_tag("li", {}, item_html))

	return render_tag("div", attrs=final_attrs, content=render_tag("ul", {}, "".join(sidebar_items)))


def render_table(headers, rows, **attrs):
	"""
	Renders MetroUI table component.

	Args:
		headers: List of table headers
		rows: List of rows (each row is a list of cells)
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "table",
		"data-role": "table"
	}

	final_attrs = {**default_attrs, **attrs}

	# Headers
	header_cells = [render_tag("th", {}, str(header)) for header in headers]
	header_row = render_tag("tr", {}, "".join(header_cells))

	# Rows
	table_rows = []
	for row in rows:
		cells = [render_tag("td", {}, str(cell)) for cell in row]
		table_rows.append(render_tag("tr", {}, "".join(cells)))

	table_body = "".join(table_rows)

	return render_tag("table", attrs=final_attrs, content=header_row + table_body)


def render_tabs(tabs, **attrs):
	"""
	Renders MetroUI tabs component.

	Args:
		tabs: List of dictionaries with 'title' and 'content' keys
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "tabs",
		"data-role": "tabs"
	}

	final_attrs = {**default_attrs, **attrs}

	# Tab navigation
	tab_nav = []
	tab_content = []

	for i, tab in enumerate(tabs):
		is_active = "active" if i == 0 else ""
		tab_nav.append(render_tag("a", {"class": f"tab {is_active}", "href": f"#tab-{i}"}, tab.get('title', '')))
		tab_content.append(
			render_tag("div", {"class": f"tab-content {is_active}", "id": f"tab-{i}"}, tab.get('content', '')))

	nav = render_tag("div", {"class": "tab-nav"}, "".join(tab_nav))
	content = render_tag("div", {"class": "tab-content-wrapper"}, "".join(tab_content))

	return render_tag("div", attrs=final_attrs, content=nav + content)


def render_toolbar(items, **attrs):
	"""
	Renders MetroUI toolbar component.

	Args:
		items: List of toolbar items
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "toolbar",
		"data-role": "toolbar"
	}

	final_attrs = {**default_attrs, **attrs}

	toolbar_items = []
	for item in items:
		if isinstance(item, dict):
			if item.get('type') == 'button':
				item_html = render_button(item.get('text', ''), **item.get('button_attrs', {}))
			else:
				item_html = render_tag("a", {"href": item.get('url', '#')}, item.get('text', ''))
		else:
			item_html = str(item)
		toolbar_items.append(render_tag("div", {"class": "toolbar-item"}, item_html))

	return render_tag("div", attrs=final_attrs, content="".join(toolbar_items))


def render_modal(title, content, **attrs):
	"""
	Renders MetroUI modal component.

	Args:
		title: Modal title
		content: Modal content
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "modal",
		"data-role": "modal"
	}

	final_attrs = {**default_attrs, **attrs}

	modal_header = render_tag("div", {"class": "modal-header"}, title)
	modal_body = render_tag("div", {"class": "modal-body"}, content)
	modal_footer = render_tag("div", {"class": "modal-footer"},
							  render_button("Close", button_type="secondary", **{"data-role": "close"}))

	modal_content = modal_header + modal_body + modal_footer

	return render_tag("div", attrs=final_attrs, content=modal_content)


def render_breadcrumb(items, **attrs):
	"""
	Renders MetroUI breadcrumb component.

	Args:
		items: List of breadcrumb items
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "breadcrumb",
		"data-role": "breadcrumb"
	}

	final_attrs = {**default_attrs, **attrs}

	breadcrumb_items = []
	for i, item in enumerate(items):
		if isinstance(item, dict):
			item_html = render_tag("a", {"href": item.get('url', '#')}, item.get('text', ''))
		else:
			item_html = str(item)

		if i < len(items) - 1:
			item_html += render_tag("span", {"class": "separator"}, "/")

		breadcrumb_items.append(render_tag("li", {}, item_html))

	return render_tag("nav", attrs=final_attrs, content=render_tag("ul", {}, "".join(breadcrumb_items)))


def render_pagination(current_page, total_pages, **attrs):
	"""
	Renders MetroUI pagination component.

	Args:
		current_page: Current page
		total_pages: Total number of pages
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "pagination",
		"data-role": "pagination"
	}

	final_attrs = {**default_attrs, **attrs}

	pagination_items = []

	# Previous button
	if current_page > 1:
		prev_item = render_tag("a", {"href": f"?page={current_page - 1}"}, "&laquo;")
		pagination_items.append(render_tag("li", {}, prev_item))

	# Page numbers
	for page in range(1, total_pages + 1):
		if page == current_page:
			page_item = render_tag("span", {"class": "current"}, str(page))
		else:
			page_item = render_tag("a", {"href": f"?page={page}"}, str(page))
		pagination_items.append(render_tag("li", {}, page_item))

	# Next button
	if current_page < total_pages:
		next_item = render_tag("a", {"href": f"?page={current_page + 1}"}, "&raquo;")
		pagination_items.append(render_tag("li", {}, next_item))

	return render_tag("nav", attrs=final_attrs, content=render_tag("ul", {}, "".join(pagination_items)))


def render_badge(content, badge_type="default", **attrs):
	"""
	Renders MetroUI badge component.

	Args:
		content: Badge content
		badge_type: Badge type (default, primary, secondary, success, danger, warning, info)
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": f"badge badge-{badge_type}"
	}

	final_attrs = {**default_attrs, **attrs}

	return render_tag("span", attrs=final_attrs, content=content)


def render_avatar(image_url, size="medium", **attrs):
	"""
	Renders MetroUI avatar component.

	Args:
		image_url: Image URL
		size: Avatar size (mini, small, medium, large)
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": f"avatar avatar-{size}",
		"data-role": "avatar"
	}

	final_attrs = {**default_attrs, **attrs}

	return render_tag("img", attrs={**final_attrs, "src": image_url, "alt": "Avatar"}, close=False)


def render_rating(value, max_value=5, **attrs):
	"""
	Renders MetroUI rating component.

	Args:
		value: Current rating
		max_value: Maximum rating
		**attrs: Additional HTML attributes
	"""
	default_attrs = {
		"class": "rating",
		"data-role": "rating",
		"data-value": str(value),
		"data-max": str(max_value)
	}

	final_attrs = {**default_attrs, **attrs}

	stars = ""
	for i in range(1, max_value + 1):
		star_class = "star" if i <= value else "star-empty"
		stars += render_tag("span", {"class": star_class}, "★")

	return render_tag("div", attrs=final_attrs, content=stars)
