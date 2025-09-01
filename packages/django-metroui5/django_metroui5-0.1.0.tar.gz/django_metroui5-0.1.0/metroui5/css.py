def _css_class_list(classes):
	"""
	Converts CSS classes to a list.

	Args:
		classes: CSS classes as string, list, or tuple

	Returns:
		List of CSS classes
	"""
	if isinstance(classes, str):
		return [cls.strip() for cls in classes.split() if cls.strip()]
	elif isinstance(classes, (list, tuple)):
		return [cls.strip() for cls in classes if cls and cls.strip()]
	else:
		return []


def merge_css_classes(*args):
	"""
	Merges CSS classes, removing duplicates and empty values.

	Args:
		*args: CSS classes as strings, lists, or tuples

	Returns:
		String with merged CSS classes
	"""
	all_classes = []
	for arg in args:
		if arg:
			all_classes.extend(_css_class_list(arg))

	# Remove duplicates while preserving order
	seen = set()
	unique_classes = []
	for cls in all_classes:
		if cls not in seen:
			seen.add(cls)
			unique_classes.append(cls)

	return " ".join(unique_classes)


def add_css_class(classes, new_class):
	"""
	Adds a new CSS class to existing ones.

	Args:
		classes: Existing CSS classes
		new_class: New CSS class to add

	Returns:
		String with updated CSS classes
	"""
	if not new_class:
		return classes

	existing_classes = _css_class_list(classes)
	if new_class not in existing_classes:
		existing_classes.append(new_class)

	return " ".join(existing_classes)


def remove_css_class(classes, class_to_remove):
	"""
	Removes CSS class from existing ones.

	Args:
		classes: Existing CSS classes
		class_to_remove: CSS class to remove

	Returns:
		String with updated CSS classes
	"""
	if not class_to_remove:
		return classes

	existing_classes = _css_class_list(classes)
	existing_classes = [cls for cls in existing_classes if cls != class_to_remove]

	return " ".join(existing_classes)
