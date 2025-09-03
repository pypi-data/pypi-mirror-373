import logging
import transaction


def setup(env):
    logging.getLogger("parso.python.diff").disabled = True
    logging.getLogger("parso.cache").disabled = True
    request = env["request"]

    # start a transaction
    request.tm.begin()

    # inject some vars into the shell builtins
    env["tm"] = request.tm
    env["dbsession"] = request.dbsession
    env["transaction"] = transaction
