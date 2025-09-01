"""
HTML utility functions for MetroUI5.
"""


def render_tag(tag, attrs=None, content=None, close=True):
	"""
	Renders HTML tag with attributes and content.

	Args:
		tag: HTML tag name
		attrs: Dictionary of attributes
		content: Tag content
		close: Whether to close the tag

	Returns:
		HTML string
	"""
	if attrs is None:
		attrs = {}

	# Build attributes string
	attr_str = ""
	for key, value in attrs.items():
		if value is not None:
			if isinstance(value, bool):
				if value:
					attr_str += f" {key}"
			else:
				attr_str += f' {key}="{value}"'

	if close:
		if content is not None:
			return f"<{tag}{attr_str}>{content}</{tag}>"
		else:
			return f"<{tag}{attr_str} />"
	else:
		return f"<{tag}{attr_str}>"


def render_link_tag(url, **attrs):
	"""
	Renders link tag for CSS file.

	Args:
		url: CSS file URL (string or dict with configuration)
		**attrs: Additional attributes

	Returns:
		HTML string for link tag
	"""
	if isinstance(url, dict):
		# Use configuration dictionary
		config = url.copy()
		href = config.pop('url', '#')
		rel = config.pop('rel', 'stylesheet')
		type_attr = config.pop('type', 'text/css')
		media = config.pop('media', 'all')

		attrs.update(config)
		attrs.update({
			'rel': rel,
			'type': type_attr,
			'media': media,
		})
	else:
		# Use simple URL string
		href = url

		if 'rel' not in attrs:
			attrs['rel'] = 'stylesheet'
		if 'type' not in attrs:
			attrs['type'] = 'text/css'

	attrs['href'] = href
	return render_tag("link", attrs, close=False)


def render_script_tag(url, **attrs):
	"""
	Renders script tag for JavaScript file.

	Args:
		url: JavaScript file URL (string or dict with configuration)
		**attrs: Additional attributes

	Returns:
		HTML string for script tag
	"""
	if isinstance(url, dict):
		# Use configuration dictionary
		config = url.copy()
		src = config.pop('url', '#')
		type_attr = config.pop('type', 'text/javascript')
		defer = config.pop('defer', False)
		async_attr = config.pop('async', False)

		attrs.update(config)
		attrs.update({
			'type': type_attr,
		})

		if defer:
			attrs['defer'] = True
		if async_attr:
			attrs['async'] = True
	else:
		# Use simple URL string
		src = url

		if 'type' not in attrs:
			attrs['type'] = 'text/javascript'

	attrs['src'] = src
	return render_tag("script", attrs, close=True)


def render_custom_css_files(css_files):
	"""
	Renders multiple custom CSS files.

	Args:
		css_files: List of CSS file configurations or URLs

	Returns:
		HTML string with multiple link tags
	"""
	if not css_files:
		return ""

	html = ""
	for css_file in css_files:
		html += render_link_tag(css_file) + "\n"

	return html.strip()


def render_custom_javascript_files(js_files):
	"""
	Renders multiple custom JavaScript files.

	Args:
		js_files: List of JavaScript file configurations or URLs

	Returns:
		HTML string with multiple script tags
	"""
	if not js_files:
		return ""

	html = ""
	for js_file in js_files:
		html += render_script_tag(js_file) + "\n"

	return html.strip()
