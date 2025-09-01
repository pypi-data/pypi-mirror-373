#!/usr/bin/env python3
"""
Setup script for django-metroui5 package.
"""

import os
from setuptools import setup, find_packages


# Read the README file
def read_readme():
	with open("README.md", "r", encoding="utf-8") as fh:
		return fh.read()


# Read requirements
def read_requirements():
	with open("requirements.txt", "r", encoding="utf-8") as fh:
		return [line.strip() for line in fh if line.strip() and not line.startswith("#")]


setup(
	name="django-metroui5",
	version="0.1.0",
	author="Maxim Harder",
	author_email="dev@devcraft.club",
	description="MetroUI v5 integration for Django 5.2.5+",
	long_description=read_readme(),
	long_description_content_type="text/markdown",
	url="https://github.com/DevCraftClub/django-metroui5",
	project_urls={
		"Bug Tracker": "https://github.com/DevCraftClub/django-metroui5/issues",
		"Documentation (Russian)": "https://readme.devcraft.club/",
		"Documentation (English)": "https://github.com/DevCraftClub/django-metroui5/docs/en/"
	},
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Environment :: Web Environment",
		"Framework :: Django",
		"Framework :: Django :: 5.2",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.13",
		"Topic :: Internet :: WWW/HTTP",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content",
		"Topic :: Software Development :: Libraries :: Python Modules",
	],
	package_dir={"": "."},
	packages=find_packages(where="."),
	include_package_data=True,
	python_requires=">=3.13",
	install_requires=[
		"Django>=5.2.5",
	],
	extras_require={
		"dev": [
			"pytest>=7.0.0",
			"pytest-django>=4.5.0",
			"black>=23.0.0",
			"flake8>=6.0.0",
			"mypy>=1.0.0",
		],
	},
	package_data={
		"metroui5": [
			"templates/**/*",
			"static/**/*",
		],
	},
	zip_safe=False,
	keywords="django, metroui, ui, frontend, framework, bootstrap-replacement",
)
