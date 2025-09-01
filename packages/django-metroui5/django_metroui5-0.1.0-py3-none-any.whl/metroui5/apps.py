from django.apps import AppConfig


class MetroUI5Config(AppConfig):
	"""
	Django MetroUI5 application configuration.
	"""
	default_auto_field = "django.db.models.BigAutoField"
	name = "metroui5"
	verbose_name = "MetroUI 5"

	def ready(self):
		"""Called when the application is ready."""
		# Here you can add additional initialization
		pass
