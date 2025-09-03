import os
import io
import pkg_resources

from typing import Tuple

HERE = os.path.abspath(os.path.dirname(__file__))


def _get_current_package_version():
    current_version = "0.0.0"
    with open(os.path.join(HERE, "../../CURRENT_VERSION")) as f:
        current_version = f.read().splitlines()[0].strip()
    return current_version


# En prod on écrit la version directement ici (car le CURRENT_VERSION n'est
# pas inclu dans les sources)
package_version = "2025.5.0b2"
# Le nom du paquet installé via pip (moogli/endi....)
egg_name = "moogli-erp"
# Le nom du package python
package_name = "caerp"


def collect_envvars_as_settings(settings, prefixes: Tuple[str] = ("CAERP_",)):
    """
    Collect environment variables in the os environment and replace the according
    setting

    Also add all vars starting with one of the prefixes to the settings (even if they are not in
     the settings). NB : only one dot is handled
    CAERP_MY_OPTION will match caerp.my_option

    Ex :

        export SQLALCHEMY_URL=mariadb+mariadbconnector://caerp:caerp@localhost/caerp?charset=utf8mb4
        export CAERP_OTHER_VAR=test
        pserve development.ini
        # will use sqlalchemy.url and caerp.other_var from environment

    """
    handled_envvars = []
    for key in settings:
        env_var_name = key.replace(".", "_").upper()
        if env_var_name in os.environ:
            handled_envvars.append(env_var_name)
            settings[key] = os.environ[env_var_name]

    for key in os.environ:
        if key in handled_envvars:
            continue

        for prefix in prefixes:
            # On rajoute le underscore si besoin
            if "_" not in prefix:
                prefix = f"{prefix}_"

            if key.startswith(prefix):
                # CAERP_ -> CAERP.
                replacement = prefix.replace("_", ".", 1)
                settings_key = key.replace(prefix, replacement).lower()
                settings[settings_key] = os.environ[key]
                break
    return settings


def resource_filename(filename: str) -> str:
    """
    Return the absolute path to the resource, works for dev and for PyInstaller
    """
    return pkg_resources.resource_filename(package_name, filename)


def resource_stream(filename: str) -> io.IOBase:
    return open(resource_filename(filename), "rb")
