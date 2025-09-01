from django.forms import BoundField

from .core import get_metroui5_setting
from .css import merge_css_classes
from .html import render_tag


class BaseRenderer:
	"""Base class for all MetroUI renderers."""

	def __init__(self, form_or_field, **kwargs):
		self.form_or_field = form_or_field
		self.kwargs = kwargs
		self.layout = kwargs.get("layout", "")
		self.size = kwargs.get("size", "")
		self.horizontal_label_class = kwargs.get(
			"horizontal_label_class",
			get_metroui5_setting("horizontal_label_class")
		)
		self.horizontal_field_class = kwargs.get(
			"horizontal_field_class",
			get_metroui5_setting("horizontal_field_class")
		)
		self.horizontal_field_offset_class = kwargs.get(
			"horizontal_field_offset_class",
			get_metroui5_setting("horizontal_field_offset_class")
		)
		self.wrapper_class = kwargs.get(
			"wrapper_class",
			get_metroui5_setting("wrapper_class")
		)
		self.inline_wrapper_class = kwargs.get(
			"inline_wrapper_class",
			get_metroui5_setting("inline_wrapper_class")
		)
		self.set_placeholder = kwargs.get(
			"set_placeholder",
			get_metroui5_setting("set_placeholder")
		)
		self.required_css_class = kwargs.get(
			"required_css_class",
			get_metroui5_setting("required_css_class")
		)
		self.error_css_class = kwargs.get(
			"error_css_class",
			get_metroui5_setting("error_css_class")
		)
		self.success_css_class = kwargs.get(
			"success_css_class",
			get_metroui5_setting("success_css_class")
		)

	def get_widget_attrs(self, widget):
		"""Gets widget attributes with MetroUI classes."""
		attrs = widget.attrs.copy()

		# Add base MetroUI classes
		base_classes = ["input"]
		if hasattr(widget, "input_type"):
			if widget.input_type == "checkbox":
				base_classes = ["checkbox"]
			elif widget.input_type == "radio":
				base_classes = ["radio"]
			elif widget.input_type == "file":
				base_classes = ["file-input"]

		# Add size if specified
		if self.size:
			base_classes.append(f"input-{self.size}")

		# Merge with existing classes
		attrs["class"] = merge_css_classes(base_classes, attrs.get("class", ""))

		# Add placeholder if enabled
		if self.set_placeholder and not attrs.get("placeholder"):
			attrs["placeholder"] = widget.attrs.get("placeholder", "")

		return attrs

	def get_field_classes(self, field):
		"""Gets CSS classes for form field."""
		classes = []

		# Add class for required fields
		if field.field.required and self.required_css_class:
			classes.append(self.required_css_class)

		# Add classes for errors and success
		if field.errors and self.error_css_class:
			classes.append(self.error_css_class)
		elif field.value() and not field.errors and self.success_css_class:
			classes.append(self.success_css_class)

		return " ".join(classes)

	def render_errors(self, errors):
		"""Renders field errors."""
		if not errors:
			return ""

		error_html = ""
		for error in errors:
			error_html += render_tag("small", {
				"class": "error-message",
				"data-role": "hint",
				"data-hint-text": str(error)
			}, str(error))

		return error_html

	def render_help_text(self, help_text):
		"""Renders help text for field."""
		if not help_text:
			return ""

		return render_tag("small", {
			"class": "help-text",
			"data-role": "hint",
			"data-hint-text": str(help_text)
		}, str(help_text))


class FieldRenderer(BaseRenderer):
	"""Renderer for individual form fields."""

	def __init__(self, field, **kwargs):
		super().__init__(field, **kwargs)
		self.field = field

	def render(self):
		"""Renders form field in MetroUI markup."""
		if not isinstance(self.field, BoundField):
			return str(self.field)

		field_html = ""

		# Render label
		if self.layout != "horizontal":
			field_html += self.render_label()

		# Render widget
		field_html += self.render_widget()

		# Render errors
		field_html += self.render_errors(self.field.errors)

		# Render help text
		field_html += self.render_help_text(self.field.help_text)

		# Wrap in container
		wrapper_class = self.wrapper_class
		if self.layout == "horizontal":
			wrapper_class = merge_css_classes(
				wrapper_class,
				self.horizontal_field_class
			)

		return render_tag("div", {
			"class": wrapper_class
		}, field_html)

	def render_label(self):
		"""Renders field label."""
		if not self.field.label:
			return ""

		label_class = "form-label"
		if self.layout == "horizontal":
			label_class = merge_css_classes(
				label_class,
				self.horizontal_label_class
			)

		return render_tag("label", {
			"for": self.field.id_for_label,
			"class": label_class
		}, self.field.label)

	def render_widget(self):
		"""Renders field widget."""
		widget = self.field.field.widget
		attrs = self.get_widget_attrs(widget)

		# Add field classes
		field_classes = self.get_field_classes(self.field)
		if field_classes:
			attrs["class"] = merge_css_classes(attrs.get("class", ""), field_classes)

		# Render widget
		return self.field.as_widget(attrs=attrs)


class FormRenderer(BaseRenderer):
	"""Renderer for forms."""

	def __init__(self, form, **kwargs):
		super().__init__(form, **kwargs)
		self.form = form

	def render(self):
		"""Renders form in MetroUI markup."""
		form_html = ""

		# Render form errors
		if self.form.non_field_errors():
			form_html += self.render_non_field_errors()

		# Render hidden fields
		form_html += self.render_hidden_fields()

		# Render visible fields
		form_html += self.render_visible_fields()

		# Wrap in form
		form_attrs = {
			"method": self.form.method or "post",
			"class": "form"
		}

		if self.form.action:
			form_attrs["action"] = self.form.action

		if self.form.is_multipart:
			form_attrs["enctype"] = "multipart/form-data"

		return render_tag("form", form_attrs, form_html)

	def render_non_field_errors(self):
		"""Renders form errors (not related to fields)."""
		errors_html = ""
		for error in self.form.non_field_errors():
			errors_html += render_tag("div", {
				"class": "alert alert-danger",
				"role": "alert"
			}, str(error))

		return errors_html

	def render_hidden_fields(self):
		"""Renders hidden form fields."""
		hidden_html = ""
		for field in self.form.hidden_fields():
			hidden_html += field.as_hidden()

		return hidden_html

	def render_visible_fields(self):
		"""Renders visible form fields."""
		fields_html = ""

		for field in self.form.visible_fields():
			field_renderer = FieldRenderer(field, **self.kwargs)
			fields_html += field_renderer.render()

		return fields_html

	def render_errors(self, type="all"):
		"""Renders form errors."""
		if type == "all":
			return self.render()
		elif type == "non_field":
			return self.render_non_field_errors()
		else:
			return ""


class FormsetRenderer(BaseRenderer):
	"""Renderer for formsets."""

	def __init__(self, formset, **kwargs):
		super().__init__(formset, **kwargs)
		self.formset = formset

	def render(self):
		"""Renders formset in MetroUI markup."""
		formset_html = ""

		# Render formset errors
		if self.formset.non_form_errors():
			formset_html += self.render_formset_errors()

		# Render forms
		for form in self.formset.forms:
			form_renderer = FormRenderer(form, **self.kwargs)
			formset_html += form_renderer.render()

		# Render formset management
		formset_html += self.render_management_form()

		return formset_html

	def render_formset_errors(self):
		"""Renders formset errors."""
		errors_html = ""
		for error in self.formset.non_form_errors():
			errors_html += render_tag("div", {
				"class": "alert alert-danger",
				"role": "alert"
			}, str(error))

		return errors_html

	def render_management_form(self):
		"""Renders formset management form."""
		return self.formset.management_form.as_p()

	def render_errors(self):
		"""Renders formset errors."""
		return self.render_formset_errors()
