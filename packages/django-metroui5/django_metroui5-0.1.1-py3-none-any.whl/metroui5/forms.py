from .core import get_field_renderer, get_form_renderer, get_formset_renderer
from .html import render_tag


def render_formset(formset, **kwargs):
	"""Renders formset in MetroUI markup."""
	renderer_cls = get_formset_renderer(**kwargs)
	return renderer_cls(formset, **kwargs).render()


def render_formset_errors(formset, **kwargs):
	"""Renders formset errors in MetroUI markup."""
	renderer_cls = get_formset_renderer(**kwargs)
	return renderer_cls(formset, **kwargs).render_errors()


def render_form(form, **kwargs):
	"""Renders form in MetroUI markup."""
	renderer_cls = get_form_renderer(**kwargs)
	return renderer_cls(form, **kwargs).render()


def render_form_errors(form, *, type="all", **kwargs):
	"""Renders form errors in MetroUI markup."""
	renderer_cls = get_form_renderer(**kwargs)
	return renderer_cls(form, **kwargs).render_errors(type)


def render_field(field, **kwargs):
	"""Renders form field in MetroUI markup."""
	renderer_cls = get_field_renderer(**kwargs)
	return renderer_cls(field, **kwargs).render()


def render_label(
		content,
		*,
		label_for=None,
		label_class="form-label",
		label_title="",
):
	"""Renders label with content."""
	attrs = {}
	if label_for:
		attrs["for"] = label_for
	if label_class:
		attrs["class"] = label_class
	if label_title:
		attrs["title"] = label_title
	return render_tag("label", attrs=attrs, content=content)
