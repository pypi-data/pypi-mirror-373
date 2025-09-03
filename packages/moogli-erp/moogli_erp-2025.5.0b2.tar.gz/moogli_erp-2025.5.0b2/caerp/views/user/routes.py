import os


USER_URL = "/users"
USER_CONNECTIONS = os.path.join(USER_URL, "connections")
USER_ADD_URL = os.path.join(USER_URL, "add")
USER_ADD_MANAGER_URL = os.path.join(USER_ADD_URL, "manager")
USER_ITEM_URL = os.path.join(USER_URL, "{id}")
USER_ACCOUNTING_URL = os.path.join(USER_ITEM_URL, "accounting")
USER_MYACCOUNT_URL = os.path.join(USER_ITEM_URL, "myaccount")
USER_ITEM_EDIT_URL = os.path.join(USER_ITEM_URL, "edit")
USER_LOGIN_URL = os.path.join(USER_ITEM_URL, "login")
USER_LOGIN_ADD_URL = os.path.join(USER_LOGIN_URL, "add")
USER_LOGIN_EDIT_URL = os.path.join(USER_LOGIN_URL, "edit")
USER_LOGIN_DISABLE_URL = os.path.join(USER_LOGIN_URL, "disable")
USER_LOGIN_SET_PASSWORD_URL = os.path.join(USER_LOGIN_URL, "set_password")

# LOGIN_URL = "/logins"
# LOGIN_ITEM_URL = os.path.join(LOGIN_URL, "{id}")
# LOGIN_EDIT_URL = os.path.join(LOGIN_ITEM_URL, "edit")
# LOGIN_SET_PASSWORD_URL = os.path.join(LOGIN_ITEM_URL, "set_password")


def includeme(config):
    for route in (
        USER_URL,
        USER_ADD_MANAGER_URL,
        USER_ADD_URL,
        USER_CONNECTIONS,
    ):
        config.add_route(route, route)

    for route in (
        USER_ITEM_URL,
        USER_ACCOUNTING_URL,
        USER_MYACCOUNT_URL,
        USER_ITEM_EDIT_URL,
        USER_LOGIN_URL,
        USER_LOGIN_EDIT_URL,
        USER_LOGIN_SET_PASSWORD_URL,
        USER_LOGIN_ADD_URL,
        USER_LOGIN_DISABLE_URL,
    ):
        config.add_route(route, route, traverse="/users/{id}")
