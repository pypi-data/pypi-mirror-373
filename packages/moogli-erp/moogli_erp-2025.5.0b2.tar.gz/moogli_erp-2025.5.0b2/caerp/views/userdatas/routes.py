import os
from caerp.views import caerp_add_route
from caerp.views.user.routes import USER_ITEM_URL


USERDATAS_URL = "/userdatas"
USERDATAS_ADD_URL = os.path.join(USERDATAS_URL, "add")
USERDATAS_XLS_URL = "/userdatas.xlsx"
USERDATAS_CSV_URL = "/userdatas.csv"
USERDATAS_ODS_URL = "/userdatas.ods"


USER_USERDATAS_URL = os.path.join(USER_ITEM_URL, "userdatas")
USER_USERDATAS_ADD_URL = os.path.join(USER_USERDATAS_URL, "add")
USER_USERDATAS_DOCTYPES_URL = os.path.join(USER_USERDATAS_URL, "doctypes")
USER_USERDATAS_PY3O_URL = os.path.join(USER_USERDATAS_URL, "py3o")
USER_USERDATAS_MYDOCUMENTS_URL = os.path.join(USER_USERDATAS_URL, "mydocuments")
USER_USERDATAS_FILELIST_URL = os.path.join(USER_USERDATAS_URL, "filelist")
USER_USERDATAS_FILE_URL = os.path.join(USER_USERDATAS_FILELIST_URL, "{id2}")
USER_USERDATAS_CAREER_PATH_URL = os.path.join(USER_USERDATAS_URL, "career_path")

CAREER_PATH_URL = "/career_paths/{id}"

TEMPLATING_URL = "/templatinghistory"
TEMPLATING_ITEM_URL = os.path.join(TEMPLATING_URL, "{id}")


def includeme(config):
    for route in (
        USERDATAS_URL,
        USERDATAS_ADD_URL,
        USERDATAS_XLS_URL,
        USERDATAS_CSV_URL,
        USERDATAS_ODS_URL,
    ):
        config.add_route(route, route)

    for route in (
        USER_USERDATAS_URL,
        USER_USERDATAS_ADD_URL,
        USER_USERDATAS_DOCTYPES_URL,
        USER_USERDATAS_PY3O_URL,
        USER_USERDATAS_MYDOCUMENTS_URL,
        USER_USERDATAS_FILELIST_URL,
        USER_USERDATAS_CAREER_PATH_URL,
    ):
        config.add_route(route, route, traverse="/users/{id}")

    caerp_add_route(config, TEMPLATING_URL)
    caerp_add_route(config, TEMPLATING_ITEM_URL, traverse="/templatinghistory/{id}")
    caerp_add_route(config, CAREER_PATH_URL, traverse="/career_path/{id}")
    caerp_add_route(config, USER_USERDATAS_FILE_URL, traverse="/files/{id2}")
