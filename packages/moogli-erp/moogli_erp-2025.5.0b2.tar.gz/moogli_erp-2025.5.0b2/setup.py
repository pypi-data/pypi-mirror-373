#!/usr/bin/env python
import os
import json
from setuptools import setup
from setuptools import find_packages


here = os.path.abspath(os.path.dirname(__file__))

if "BUILD_PACKAGE_NAME" in os.environ:
    BUILD_NAME = os.environ["BUILD_PACKAGE_NAME"]
else:
    with open(os.path.join(here, "CURRENT_PACKAGE_NAME")) as f:
        BUILD_NAME = f.read().splitlines()[0].strip()

configuration_file = os.path.join(here, f"{BUILD_NAME}_setup.json")
configuration = json.load(open(configuration_file, "r"))

with open(
    os.path.join(here, configuration["readme"].strip()), "r", encoding="utf-8"
) as f:
    README = f.read()

with open(os.path.join(here, "requirements.txt")) as f:
    install_reqs = f.read()

with open(os.path.join(here, "dev_requirements.txt")) as f:
    dev_requirements = [pkg.strip() for pkg in f.read().splitlines() if pkg.strip()]


def get_version():
    if "BUILD_VERSION" in os.environ:
        return os.environ["BUILD_VERSION"].strip()
    else:
        with open(os.path.join(here, "CURRENT_VERSION")) as f:
            current_version = f.read().splitlines()[0].strip()
        return current_version


entry_points = {
    "paste.app_factory": [
        "main=caerp:main",
    ],
    "console_scripts": [
        "caerp-migrate = caerp.scripts:migrate_entry_point",
        "caerp-admin = caerp.scripts:admin_entry_point",
        "caerp-cache = caerp.scripts:cache_entry_point",
        "caerp-clean = caerp.scripts:clean_entry_point",
        "caerp-celery = caerp.scripts:celery_command_entry_point",
        "caerp-export = caerp.scripts:export_entry_point",
        "caerp-custom = caerp.scripts.caerp_custom:custom_entry_point",
        "caerp-company-export = caerp.scripts:company_export_entry_point",
        "caerp-anonymize = caerp.scripts:anonymize_entry_point",
        "caerp-load-demo-data = caerp.scripts:load_demo_data_entry_point",
    ],
    "fanstatic.libraries": [
        "caerp = caerp.resources:lib_caerp",
        "tinymce59 = caerp.resources:tinymce_library",
    ],
}

setup(
    name=configuration["name"].strip(),
    version=get_version(),
    description="Progiciel de gestion pour CAE",
    long_description=README,
    long_description_content_type="text/x-rst",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author=configuration["author"].strip(),
    author_email=configuration["author_email"].strip(),
    url=configuration["url"].strip(),
    keywords="pyramid,business,web",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",  # keep in sync with pyproject.toml
    install_requires=install_reqs,
    tests_require=["pytest", "WebTest", "Mock"],
    extras_require={"dev": dev_requirements},
    setup_requires=[],
    test_suite="caerp.tests",
    entry_points=entry_points,
)
