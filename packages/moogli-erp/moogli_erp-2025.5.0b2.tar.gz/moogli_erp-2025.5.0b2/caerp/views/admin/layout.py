from caerp.resources import admin_resources
from caerp.utils.sys_environment import package_version


class AdminLayout:
    caerp_version = package_version

    def __init__(self, context, request):
        admin_resources.need()


def includeme(config):
    config.add_layout(
        AdminLayout,
        template="caerp:templates/admin/layout.mako",
        name="admin",
    )
