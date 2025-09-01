from importlib import import_module
from urllib.parse import urlparse

from django.conf import settings

METROUI5_DEFAULTS = {
	"css_url": {
		"url": "metroui5/css/metro.all.css",
		"integrity": None,
		"crossorigin": None,
		"type": "text/css",
		"media": "all",
	},
	"javascript_url": {
		"url": "metroui5/js/metro.all.js",
		"integrity": None,
		"crossorigin": None,
		"type": "text/javascript",
		"defer": False,
		"async": False,
	},
	"icons_css_url": {
		"url": "metroui5/icons/icons.css",
		"integrity": None,
		"crossorigin": None,
		"type": "text/css",
		"media": "all",
	},
	"javascript_in_head": False,
	"wrapper_class": "mb-3",
	"inline_wrapper_class": "",
	"horizontal_label_class": "col-sm-2",
	"horizontal_field_class": "col-sm-10",
	"horizontal_field_offset_class": "offset-sm-2",
	"set_placeholder": True,
	"checkbox_layout": None,
	"checkbox_style": None,
	"required_css_class": "required",
	"error_css_class": "error",
	"success_css_class": "success",
	"server_side_validation": True,
	"formset_renderers": {"default": "metroui5.renderers.FormsetRenderer"},
	"form_renderers": {"default": "metroui5.renderers.FormRenderer"},
	"field_renderers": {
		"default": "metroui5.renderers.FieldRenderer",
	},
	"hyphenate_attribute_prefixes": ["data"],
	"tile_size_options": ["small", "medium", "large", "wide", "tall"],
	"tile_color_options": ["blue", "green", "red", "yellow", "orange", "purple", "pink", "brown", "gray"],
	# Additional CSS/JS customization options
	"custom_css_files": [],
	"custom_javascript_files": [],
	"cdn_mode": False,
	"minified": True,
	# CDN configuration
	"use_cdn": False,
	"default_cdn_js": "https://cdn.metroui.org.ua/current/metro.js",
	"default_cdn_css": "https://cdn.metroui.org.ua/current/metro.css",
	"default_cdn_icons": "https://cdn.metroui.org.ua/current/icons.css",
	"cdn_js_url": None,
	"cdn_css_url": None,
	"cdn_icons_url": None,
	# Theme configuration
	"theme": "light",  # 'light', 'dark', or 'auto'
	"theme_target": "html",  # Target element for theme class (default: 'html')
	"theme_switcher_enabled": False,  # Enable built-in theme switcher
}


def get_metroui5_setting(name, default=None):
	"""
	Reads MetroUI5 setting.

	Search order:

	1. Django settings
	2. django-metroui5 default values
	3. Passed default value
	"""
	metroui5_settings = getattr(settings, "METROUI5", {})
	return metroui5_settings.get(name, METROUI5_DEFAULTS.get(name, default))


def _validate_url_config(config, config_type):
	"""
	Validates URL configuration for CSS/JS files.

	Args:
		config: Configuration dictionary
		config_type: Type of configuration ('css', 'javascript', 'icons')

	Returns:
		dict: Validated configuration
	"""
	if not isinstance(config, dict):
		raise ValueError(f"METROUI5 {config_type}_url must be a dictionary")

	# Ensure required 'url' key exists
	if 'url' not in config:
		raise ValueError(f"METROUI5 {config_type}_url must contain 'url' key")

	# Validate URL format
	url = config['url']
	if not url:
		raise ValueError(f"METROUI5 {config_type}_url 'url' cannot be empty")

	# Check if it's an external URL or local static file
	parsed_url = urlparse(url)
	is_external = bool(parsed_url.scheme and parsed_url.netloc)

	# For external URLs, ensure crossorigin is set if integrity is provided
	if is_external and config.get('integrity') and not config.get('crossorigin'):
		config['crossorigin'] = 'anonymous'

	return config


def _get_file_url(config, config_type):
	"""
	Gets the appropriate URL for a file configuration.

	Args:
		config: File configuration dictionary
		config_type: Type of configuration ('css', 'javascript', 'icons')

	Returns:
		dict: Configuration with processed URL
	"""
	config = _validate_url_config(config, config_type)
	url = config['url']

	# If it's a local static file (no scheme), ensure it starts with static prefix
	parsed_url = urlparse(url)
	if not parsed_url.scheme and not parsed_url.netloc:
		# Local static file - ensure it has proper static prefix
		if not url.startswith(('http://', 'https://', '//', '/static/', 'static/')):
			# Add static prefix if not already present
			if not url.startswith('/'):
				url = f'/static/{url}'
			else:
				url = f'/static{url}'
		config['url'] = url

	return config


def javascript_url():
	"""Returns the full URL to the MetroUI JavaScript file."""
	if get_metroui5_setting("use_cdn", False):
		# CDN режим - используем пользовательские URL или дефолтные
		cdn_url = get_metroui5_setting("cdn_js_url")
		if cdn_url:
			return {
				"url": cdn_url,
				"integrity": None,
				"crossorigin": "anonymous",
				"type": "text/javascript",
				"defer": False,
				"async": False,
			}
		else:
			# Используем дефолтный CDN URL
			return {
				"url": get_metroui5_setting("default_cdn_js"),
				"integrity": None,
				"crossorigin": "anonymous",
				"type": "text/javascript",
				"defer": False,
				"async": False,
			}
	else:
		# Локальный режим
		config = get_metroui5_setting("javascript_url")
		return _get_file_url(config, "javascript")


def css_url():
	"""Returns the full URL to the MetroUI CSS file."""
	if get_metroui5_setting("use_cdn", False):
		# CDN режим - используем пользовательские URL или дефолтные
		cdn_url = get_metroui5_setting("cdn_css_url")
		if cdn_url:
			return {
				"url": cdn_url,
				"integrity": None,
				"crossorigin": "anonymous",
				"type": "text/css",
				"media": "all",
			}
		else:
			# Используем дефолтный CDN URL
			return {
				"url": get_metroui5_setting("default_cdn_css"),
				"integrity": None,
				"crossorigin": "anonymous",
				"type": "text/css",
				"media": "all",
			}
	else:
		# Локальный режим
		config = get_metroui5_setting("css_url")
		return _get_file_url(config, "css")


def icons_css_url():
	"""Returns the full URL to the MetroUI icons CSS file."""
	if get_metroui5_setting("use_cdn", False):
		# CDN режим - используем пользовательские URL или дефолтные
		cdn_url = get_metroui5_setting("cdn_icons_url")
		if cdn_url:
			return {
				"url": cdn_url,
				"integrity": None,
				"crossorigin": "anonymous",
				"type": "text/css",
				"media": "all",
			}
		else:
			# Используем дефолтный CDN URL
			return {
				"url": get_metroui5_setting("default_cdn_icons"),
				"integrity": None,
				"crossorigin": "anonymous",
				"type": "text/css",
				"media": "all",
			}
	else:
		# Локальный режим
		config = get_metroui5_setting("icons_css_url")
		return _get_file_url(config, "icons")


def custom_css_files():
	"""Returns list of custom CSS files to include."""
	return get_metroui5_setting("custom_css_files", [])


def custom_javascript_files():
	"""Returns list of custom JavaScript files to include."""
	return get_metroui5_setting("custom_javascript_files", [])


def is_cdn_mode():
	"""Returns whether CDN mode is enabled."""
	return get_metroui5_setting("cdn_mode", False)


def is_use_cdn():
	"""Returns whether CDN mode is enabled (new implementation)."""
	return get_metroui5_setting("use_cdn", False)


def get_theme():
	"""Returns the current theme setting."""
	return get_metroui5_setting("theme", "light")


def get_theme_target():
	"""Returns the target element for theme class."""
	return get_metroui5_setting("theme_target", "html")


def is_theme_switcher_enabled():
	"""Returns whether theme switcher is enabled."""
	return get_metroui5_setting("theme_switcher_enabled", False)


def get_theme_meta_tag():
	"""Returns the meta tag for theme configuration."""
	theme = get_theme()
	if theme in ["light", "dark", "auto"]:
		return f'<meta name="metroui:theme" content="{theme}">'
	return ""


def get_theme_class():
	"""Returns the theme class to apply to the target element."""
	theme = get_theme()
	if theme == "dark":
		return "dark-side"
	return ""


def get_theme_switcher_html():
	"""Returns HTML for the theme switcher component."""
	if not is_theme_switcher_enabled():
		return ""

	theme_target = get_theme_target()
	target_attr = f'data-target="{theme_target}"' if theme_target != "html" else ""

	return f'''
    <div class="theme-switcher-container">
        <input type="checkbox" data-role="theme-switcher" {target_attr}>
        <label for="theme-switcher">Toggle Theme</label>
    </div>
    '''


def get_renderer(renderers, **kwargs):
	"""Gets renderer by name or uses default value."""
	layout = kwargs.get("layout", "")
	path = renderers.get(layout, renderers["default"])
	mod, cls = path.rsplit(".", 1)
	return getattr(import_module(mod), cls)


def get_formset_renderer(**kwargs):
	"""Gets renderer for formsets."""
	renderers = get_metroui5_setting("formset_renderers")
	return get_renderer(renderers, **kwargs)


def get_form_renderer(**kwargs):
	"""Gets renderer for forms."""
	renderers = get_metroui5_setting("form_renderers")
	return get_renderer(renderers, **kwargs)


def get_field_renderer(**kwargs):
	"""Gets renderer for form fields."""
	renderers = get_metroui5_setting("field_renderers")
	return get_renderer(renderers, **kwargs)
