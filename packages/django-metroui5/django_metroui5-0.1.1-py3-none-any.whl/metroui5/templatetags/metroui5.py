from django import template
from django.contrib.messages import constants as message_constants
from django.utils.safestring import mark_safe

from ..components import (
	render_alert, render_button, render_tile, render_card, render_progress,
	render_accordion, render_calendar, render_dialog, render_dropdown,
	render_input, render_list, render_menu, render_navigation, render_panel,
	render_sidebar, render_table, render_tabs, render_toolbar, render_modal,
	render_breadcrumb, render_pagination, render_badge, render_avatar, render_rating
)
from ..core import css_url, get_metroui5_setting, javascript_url, icons_css_url
from ..css import merge_css_classes
from ..forms import (
	render_field, render_form, render_form_errors, render_formset, )
from ..html import render_link_tag, render_script_tag, render_tag

MESSAGE_ALERT_TYPES = {
	message_constants.DEBUG: "warning", message_constants.INFO: "info",
	message_constants.SUCCESS: "success", message_constants.WARNING: "warning",
	message_constants.ERROR: "danger",
}

register = template.Library()


@register.simple_tag
def metroui5_setting(value):
	"""Returns MetroUI5 setting value."""
	return get_metroui5_setting(value)


@register.simple_tag
def metroui5_css_url():
	"""Returns URL for MetroUI CSS file."""
	return css_url()


@register.simple_tag
def metroui5_javascript_url():
	"""Returns URL for MetroUI JavaScript file."""
	return javascript_url()


@register.simple_tag
def metroui5_icons_css_url():
	"""Returns URL for MetroUI icons CSS file."""
	return icons_css_url()


@register.simple_tag
def metroui5_css():
	"""Includes MetroUI CSS file."""
	return mark_safe(render_link_tag(css_url()))


@register.simple_tag
def metroui5_javascript():
	"""Includes MetroUI JavaScript file."""
	return mark_safe(render_script_tag(javascript_url()))


@register.simple_tag
def metroui5_icons_css():
	"""Includes MetroUI icons CSS file."""
	return mark_safe(render_link_tag(icons_css_url()))


@register.simple_tag
def metroui5_custom_css():
	"""Includes custom CSS files specified in settings."""
	from metroui5.html import render_custom_css_files
	from metroui5.core import custom_css_files

	return mark_safe(render_custom_css_files(custom_css_files()))


@register.simple_tag
def metroui5_custom_javascript():
	"""Includes custom JavaScript files specified in settings."""
	from metroui5.html import render_custom_javascript_files
	from metroui5.core import custom_javascript_files

	return mark_safe(render_custom_javascript_files(custom_javascript_files()))


@register.simple_tag
def metroui5_all_css():
	"""Includes all MetroUI CSS files (core + custom)."""
	from metroui5.html import render_custom_css_files
	from metroui5.core import custom_css_files

	html = metroui5_css()

	# Add custom CSS files
	custom_css = render_custom_css_files(custom_css_files())
	if custom_css:
		html += "\n" + custom_css

	return mark_safe(html)


@register.simple_tag
def metroui5_all_javascript():
	"""Includes all MetroUI JavaScript files (core + custom)."""
	from metroui5.html import render_custom_javascript_files
	from metroui5.core import custom_javascript_files

	html = metroui5_javascript()

	# Add custom JavaScript files
	custom_js = render_custom_javascript_files(custom_javascript_files())
	if custom_js:
		html += "\n" + custom_js

	return mark_safe(html)


@register.simple_tag
def metroui5_cdn_mode():
	"""Returns whether CDN mode is enabled."""
	from metroui5.core import is_cdn_mode
	return is_cdn_mode()


@register.simple_tag
def metroui5_form(form, **kwargs):
	"""Renders form with MetroUI styling."""
	return mark_safe(render_form(form, **kwargs))


@register.simple_tag
def metroui5_field(field, **kwargs):
	"""Renders form field with MetroUI styling."""
	return mark_safe(render_field(field, **kwargs))


@register.simple_tag
def metroui5_form_errors(form, **kwargs):
	"""Renders form errors in MetroUI style."""
	return mark_safe(render_form_errors(form, **kwargs))


@register.simple_tag
def metroui5_formset(formset, **kwargs):
	"""Renders formset with MetroUI styling."""
	return mark_safe(render_formset(formset, **kwargs))


@register.simple_tag
def metroui5_button(content, **kwargs):
	"""Renders MetroUI button."""
	return mark_safe(render_button(content, **kwargs))


@register.simple_tag
def metroui5_tile(title, **kwargs):
	"""Renders MetroUI tile."""
	return mark_safe(render_tile(title, **kwargs))


@register.simple_tag
def metroui5_card(**kwargs):
	"""Renders MetroUI card."""
	return mark_safe(render_card(**kwargs))


@register.simple_tag
def metroui5_progress(value, **kwargs):
	"""Renders MetroUI progress bar."""
	return mark_safe(render_progress(value, **kwargs))


@register.simple_tag
def metroui5_alert(content, **kwargs):
	"""Renders MetroUI alert."""
	return mark_safe(render_alert(content, **kwargs))


@register.simple_tag
def metroui5_messages(*args, **kwargs):
	"""Renders Django messages in MetroUI style."""
	from django.contrib.messages import get_messages

	messages = get_messages(kwargs.get('request'))
	if not messages:
		return ""

	alerts = []
	for message in messages:
		alert_type = metroui5_message_alert_type(message)
		alerts.append(render_alert(str(message), alert_type=alert_type))

	return mark_safe("".join(alerts))


@register.filter
def metroui5_message_alert_type(message):
	"""Returns alert type for Django message."""
	return MESSAGE_ALERT_TYPES.get(message.level, "info")


@register.simple_tag
def metroui5_classes(*args):
	"""Combines CSS classes."""
	return merge_css_classes(*args)


# New template tags for advanced components

@register.simple_tag
def metroui5_accordion(items, **kwargs):
	"""Renders MetroUI accordion."""
	return mark_safe(render_accordion(items, **kwargs))


@register.simple_tag
def metroui5_calendar(**kwargs):
	"""Renders MetroUI calendar."""
	return mark_safe(render_calendar(**kwargs))


@register.simple_tag
def metroui5_dialog(title, content, **kwargs):
	"""Renders MetroUI dialog."""
	return mark_safe(render_dialog(title, content, **kwargs))


@register.simple_tag
def metroui5_dropdown(items, button_text="Dropdown", **kwargs):
	"""Renders MetroUI dropdown."""
	return mark_safe(render_dropdown(items, button_text, **kwargs))


@register.simple_tag
def metroui5_input(input_type="text", placeholder="", **kwargs):
	"""Renders MetroUI input."""
	return mark_safe(render_input(input_type, placeholder, **kwargs))


@register.simple_tag
def metroui5_list(items, list_type="ul", **kwargs):
	"""Renders MetroUI list."""
	return mark_safe(render_list(items, list_type, **kwargs))


@register.simple_tag
def metroui5_menu(items, **kwargs):
	"""Renders MetroUI menu."""
	return mark_safe(render_menu(items, **kwargs))


@register.simple_tag
def metroui5_navigation(items, **kwargs):
	"""Renders MetroUI navigation."""
	return mark_safe(render_navigation(items, **kwargs))


@register.simple_tag
def metroui5_panel(title=None, content=None, **kwargs):
	"""Renders MetroUI panel."""
	return mark_safe(render_panel(title, content, **kwargs))


@register.simple_tag
def metroui5_sidebar(items, **kwargs):
	"""Renders MetroUI sidebar."""
	return mark_safe(render_sidebar(items, **kwargs))


@register.simple_tag
def metroui5_table(headers, rows, **kwargs):
	"""Renders MetroUI table."""
	return mark_safe(render_table(headers, rows, **kwargs))


@register.simple_tag
def metroui5_tabs(tabs, **kwargs):
	"""Renders MetroUI tabs."""
	return mark_safe(render_tabs(tabs, **kwargs))


@register.simple_tag
def metroui5_toolbar(items, **kwargs):
	"""Renders MetroUI toolbar."""
	return mark_safe(render_toolbar(items, **kwargs))


@register.simple_tag
def metroui5_modal(title, content, **kwargs):
	"""Renders MetroUI modal."""
	return mark_safe(render_modal(title, content, **kwargs))


@register.simple_tag
def metroui5_breadcrumb(items, **kwargs):
	"""Renders MetroUI breadcrumb."""
	return mark_safe(render_breadcrumb(items, **kwargs))


@register.simple_tag
def metroui5_pagination(current_page, total_pages, **kwargs):
	"""Renders MetroUI pagination."""
	return mark_safe(render_pagination(current_page, total_pages, **kwargs))


@register.simple_tag
def metroui5_badge(content, badge_type="default", **kwargs):
	"""Renders MetroUI badge."""
	return mark_safe(render_badge(content, badge_type, **kwargs))


@register.simple_tag
def metroui5_avatar(image_url, size="medium", **kwargs):
	"""Renders MetroUI avatar."""
	return mark_safe(render_avatar(image_url, size, **kwargs))


@register.simple_tag
def metroui5_rating(value, max_value=5, **kwargs):
	"""Renders MetroUI rating."""
	return mark_safe(render_rating(value, max_value, **kwargs))


# Utility template tags

@register.simple_tag
def metroui5_icon(icon_name, size=None, **kwargs):
	"""Renders MetroUI icon."""
	icon_classes = ["mif", icon_name]
	if size:
		icon_classes.append(f"mif-{size}")

	attrs = {"class": " ".join(icon_classes)}
	attrs.update(kwargs)

	return mark_safe(render_tag("span", attrs=attrs, content=""))


@register.simple_tag
def metroui5_grid(columns=12, **kwargs):
	"""Renders MetroUI grid container."""
	attrs = {"class": f"grid grid-{columns}"}
	attrs.update(kwargs)

	return mark_safe(render_tag("div", attrs=attrs, content=""))


@register.simple_tag
def metroui5_row(**kwargs):
	"""Renders MetroUI row."""
	attrs = {"class": "row"}
	attrs.update(kwargs)

	return mark_safe(render_tag("div", attrs=attrs, content=""))


@register.simple_tag
def metroui5_cell(size, **kwargs):
	"""Renders MetroUI cell."""
	attrs = {"class": f"cell-{size}"}
	attrs.update(kwargs)

	return mark_safe(render_tag("div", attrs=attrs, content=""))


@register.simple_tag
def metroui5_container(**kwargs):
	"""Renders MetroUI container."""
	attrs = {"class": "container"}
	attrs.update(kwargs)

	return mark_safe(render_tag("div", attrs=attrs, content=""))


@register.simple_tag
def metroui5_fluid_container(**kwargs):
	"""Renders MetroUI fluid container."""
	attrs = {"class": "container-fluid"}
	attrs.update(kwargs)

	return mark_safe(render_tag("div", attrs=attrs, content=""))





@register.simple_tag
def metroui5_app_bar(**kwargs):
	"""Renders MetroUI app bar."""
	attrs = {"class": "app-bar", "data-role": "appbar"}
	attrs.update(kwargs)

	return mark_safe(render_tag("div", attrs=attrs, content=""))


@register.simple_tag
def metroui5_notify(message, **kwargs):
	"""Renders MetroUI notify."""
	attrs = {"class": "notify", "data-role": "notify"}
	attrs.update(kwargs)

	return mark_safe(render_tag("div", attrs=attrs, content=message))


@register.simple_tag
def metroui5_hint(text, **kwargs):
	"""Renders MetroUI hint."""
	attrs = {"class": "hint", "data-role": "hint", "data-hint-text": text}
	attrs.update(kwargs)

	return mark_safe(render_tag("div", attrs=attrs, content=""))


@register.simple_tag
def metroui5_loading(**kwargs):
	"""Renders MetroUI loading indicator."""
	attrs = {"class": "loading", "data-role": "loading"}
	attrs.update(kwargs)

	return mark_safe(render_tag("div", attrs=attrs, content=""))


@register.simple_tag
def metroui5_spinner(**kwargs):
	"""Renders MetroUI spinner."""
	attrs = {"class": "spinner", "data-role": "spinner"}
	attrs.update(kwargs)

	return mark_safe(render_tag("div", attrs=attrs, content=""))


@register.simple_tag
def metroui5_stepper(steps, **kwargs):
	"""Renders MetroUI stepper."""
	attrs = {"class": "stepper", "data-role": "stepper"}
	attrs.update(kwargs)

	stepper_items = []
	for i, step in enumerate(steps):
		step_class = "active" if i == 0 else ""
		step_html = render_tag("div", {"class": f"step {step_class}"}, step)
		stepper_items.append(step_html)

	return mark_safe(render_tag("div", attrs=attrs, content="".join(stepper_items)))


@register.simple_tag
def metroui5_tree(items, **kwargs):
	"""Renders MetroUI tree."""
	attrs = {"class": "tree", "data-role": "tree"}
	attrs.update(kwargs)

	def render_tree_item(item):
		if isinstance(item, dict):
			item_html = render_tag("span", {}, item.get('text', ''))
			if 'children' in item:
				children_html = "".join([render_tree_item(child) for child in item['children']])
				item_html += render_tag("ul", {}, children_html)
			return render_tag("li", {}, item_html)
		else:
			return render_tag("li", {}, str(item))

	tree_items = [render_tree_item(item) for item in items]

	return mark_safe(render_tag("div", attrs=attrs, content=render_tag("ul", {}, "".join(tree_items))))


@register.simple_tag
def metroui5_wizard(steps, **kwargs):
	"""Renders MetroUI wizard."""
	attrs = {"class": "wizard", "data-role": "wizard"}
	attrs.update(kwargs)

	wizard_nav = []
	wizard_content = []

	for i, step in enumerate(steps):
		is_active = "active" if i == 0 else ""
		step_title = step.get('title', f'Step {i + 1}')
		step_content = step.get('content', '')

		wizard_nav.append(render_tag("a", {"class": f"step {is_active}", "href": f"#step-{i}"}, step_title))
		wizard_content.append(
			render_tag("div", {"class": f"step-content {is_active}", "id": f"step-{i}"}, step_content))

	nav = render_tag("div", {"class": "wizard-nav"}, "".join(wizard_nav))
	content = render_tag("div", {"class": "wizard-content"}, "".join(wizard_content))

	return mark_safe(render_tag("div", attrs=attrs, content=nav + content))


@register.simple_tag
def metroui5_theme_meta():
	"""Returns the meta tag for theme configuration."""
	from metroui5.core import get_theme_meta_tag
	return get_theme_meta_tag()


@register.simple_tag
def metroui5_theme_class():
	"""Returns the theme class to apply to the target element."""
	from metroui5.core import get_theme_class
	return get_theme_class()


@register.simple_tag
def metroui5_theme_switcher():
	"""Returns HTML for the theme switcher component."""
	from metroui5.core import get_theme_switcher_html
	return mark_safe(get_theme_switcher_html())


@register.simple_tag
def metroui5_theme_switcher_switch():
	"""Returns HTML for the theme switcher in switch mode."""
	from metroui5.core import is_theme_switcher_enabled, get_theme_target
	if not is_theme_switcher_enabled():
		return ""

	theme_target = get_theme_target()
	target_attr = f'data-target="{theme_target}"' if theme_target != "html" else ""

	return mark_safe(f'<input type="checkbox" data-role="theme-switcher" {target_attr}>')


@register.simple_tag
def metroui5_theme_switcher_button():
	"""Returns HTML for the theme switcher in button mode."""
	from metroui5.core import is_theme_switcher_enabled, get_theme_target
	if not is_theme_switcher_enabled():
		return ""

	theme_target = get_theme_target()
	target_attr = f'data-target="{theme_target}"' if theme_target != "html" else ""

	return mark_safe(f'<input type="checkbox" data-role="theme-switcher" data-mode="button" {target_attr}>')


@register.simple_tag
def metroui5_theme_info():
	"""Returns theme information for debugging."""
	from metroui5.core import get_theme, get_theme_target, is_theme_switcher_enabled
	return {
		'theme': get_theme(),
		'target': get_theme_target(),
		'switcher_enabled': is_theme_switcher_enabled(),
	}
