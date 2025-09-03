from caerp.consts.permissions import PERMISSIONS
from pyramid.request import Request


def get_visibility_options(request: Request) -> dict:
    perms = [
        dict(value="public", label="Public"),
        dict(value="private", label="Perso"),
    ]
    if request.has_permission(PERMISSIONS["global.access_ea"]):
        perms.append(dict(value="management", label="Équipe d'appui"))
    return perms
