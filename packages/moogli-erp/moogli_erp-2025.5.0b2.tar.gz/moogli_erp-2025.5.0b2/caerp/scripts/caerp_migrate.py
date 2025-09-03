"""
Migration related command line scripts for MoOGLi
"""

import os
import sys
from typing import Tuple

import pkg_resources
import logging

from pyramid.threadlocal import get_current_registry
from sqlalchemy.exc import DatabaseError
from zope.sqlalchemy import mark_changed

from caerp.alembic.exceptions import MigrationError, RollbackError
from alembic.config import Config
from alembic.script import Script, ScriptDirectory
from alembic.environment import EnvironmentContext
from alembic.util import load_python_file, rev_id, CommandError
from alembic import autogenerate as autogen, util

from caerp_base.models.base import DBSESSION
from caerp.scripts.utils import (
    command,
    get_value,
)
from caerp import version as caerp_version
from caerp.utils.sys_environment import resource_filename

MIGRATION_FAILED_MSG = "Some migration operations failed, rolled back everything…"
ROLLBACK_FAILED_MSG = (
    "Some migration operations failed and ROLL BACK FAILED."
    " Database might be in an inconsistent state."
)

MULTIPLE_HEADS_MSG = (
    "There are multiple heads."
    " Use `caerp-migrate <ini_file> merge` to create a merge revision."
)

logger = logging.getLogger("alembic.caerp")


def get_location(pkg_name):
    """
    Return the location of the alembic stuff in : separated format

    :rtype: str
    """
    return "{}:alembic".format(pkg_name)


def get_script_directory(pkg_name):
    """
    Build the script directory that should be used for migrations
    """
    return pkg_resources.resource_filename(pkg_name, "alembic")


class ScriptDirectoryWithDefaultEnvPy(ScriptDirectory):
    """
    Wrapper for the ScriptDirectory object
    enforce the env.py script
    """

    # Overrider une property ne peut se faire juste avec un setattr
    # on utilise donc un attribut custom _env_py_location
    @property
    def env_py_location(self):
        return self._env_py_location

    def run_env(self):
        dir_, filename = self.env_py_location.rsplit(os.path.sep, 1)
        load_python_file(dir_, filename)


class PackageEnvironment:
    """
    package environment
    Here we use one but it could be usefull when handling plugins'
    migrations
    """

    def __init__(self, pkg, sql_url=None):
        self.package = pkg
        self.location = get_location(pkg)
        self.config = self._make_config(sql_url)
        self.script_dir = self._make_script_dir(self.config)

    @property
    def pkg_name(self):
        return self.location.split(":")[0]

    @property
    def version_table(self):
        """
        Return the name of the table hosting alembic's current revision
        """
        # Still using "autonomie" name for backward compatibility
        if self.package == "caerp":
            return "autonomie_alembic_version"
        else:
            return "{}_alembic_version".format(self.package)

    def run_env(self, fn, **kw):
        """
        run alembic's context
        """
        with EnvironmentContext(
            self.config, self.script_dir, fn=fn, version_table=self.version_table, **kw
        ):
            self.script_dir.run_env()

    def _get_database_setting(self, settings):
        """
        Try to find out under which configuration root, the sql database url is
        stored
        """
        custom_key = "{}_db.url".format(self.package)
        if custom_key in settings:
            return settings[custom_key]
        else:
            return settings["sqlalchemy.url"]

    def _make_config(self, sql_url=None):
        """
        populate alembic's configuration
        """
        cfg = Config()
        cfg.set_main_option("script_location", self.location)
        if sql_url is None:
            settings = get_current_registry().settings
            sql_url = self._get_database_setting(settings)

        cfg.set_main_option("sqlalchemy.url", sql_url)
        version_slug = caerp_version(strip_suffix=True).replace(".", "_")
        cfg.set_main_option("file_template", version_slug + "_%%(slug)s_%%(rev)s")
        return cfg

    def _make_script_dir(self, alembic_cfg):
        """
        build and cast the script_directory
        """
        script_dir = ScriptDirectory.from_config(alembic_cfg)
        script_dir.__class__ = ScriptDirectoryWithDefaultEnvPy
        script_dir._env_py_location = os.path.join(
            get_script_directory(self.package), "env.py"
        )
        return script_dir


def upgrade_command(pkg, revision, sql_url=None):
    """
    upgrade the content of the database at sql_url
    """
    pkg_env = PackageEnvironment(pkg, sql_url)

    if revision is None:
        revision = pkg_env.script_dir.get_current_head()

    logger.info("Upgrading {0}:".format(pkg_env.location))

    def upgrade_func(rev, context):
        if len(rev) == 0:
            logger.info("No migration scripts added since install.")
            return []

        rev = rev[0]
        if rev == revision:
            logger.info("Already up to date.")
            return []
        logger.info("Upgrading from {0} to {1}...".format(rev, revision))
        return context.script._upgrade_revs(revision, rev)

    try:
        pkg_env.run_env(
            upgrade_func,
            starting_rev=None,
            destination_rev=revision,
        )

    except RollbackError:
        logger.error(ROLLBACK_FAILED_MSG)
        sys.exit(1)

    except MigrationError:
        logger.error(MIGRATION_FAILED_MSG)
        sys.exit(2)

    else:
        fetch_command(pkg, revision)
    print()


def downgrade_command(pkg, revision):
    """
    downgrade the content of DEFAULT_LOCATION
    """
    pkg_env = PackageEnvironment(pkg)

    logger.info("Downgrading {0} to {1}:".format(pkg_env.location, revision))

    def downgrade_func(rev, context):
        if rev == revision:
            logger.info("  - already reached.")
            return []
        elif revision is None:
            raise Exception("   - You should specify the down revision")
        logger.info("  - downgrading from {0} to {1}...".format(rev, revision))
        return context.script._downgrade_revs(revision, rev)

    try:
        pkg_env.run_env(
            downgrade_func,
            starting_rev=None,
            destination_rev=revision,
        )
    except RollbackError:
        logger.error(ROLLBACK_FAILED_MSG)

    except MigrationError:
        logger.error(MIGRATION_FAILED_MSG)

    else:
        fetch_command(pkg, revision)
    print()


def _get_fork_start(
    env: PackageEnvironment, rev_a_id: str, rev_b_id: str
) -> Tuple[Script, str]:
    """
    Given a revision (rev_a_id), returns the first revision that diverges with rev_b lineage
    The start of rev_a fork.
    """

    a_ancestors = env.script_dir.iterate_revisions(rev_a_id, "base")
    b_ancestors_ids = [
        rev.revision for rev in env.script_dir.iterate_revisions(rev_b_id, "base")
    ]

    for a_ancestor in a_ancestors:
        a_ancestor_parent_ids = util.to_tuple(a_ancestor.down_revision)
        for parent_rev_id in a_ancestor_parent_ids:
            if parent_rev_id in b_ancestors_ids:
                # parent_rev_id is the closest common ancestor to a and b !
                return a_ancestor, parent_rev_id


def list_command(pkg):
    """
    list all available revisions
    """
    pkg_env = PackageEnvironment(pkg)
    print(("{0}:".format(pkg_env.pkg_name)))
    revisions = list(pkg_env.script_dir.walk_revisions())
    revisions.reverse()

    def print_list(rev, context):
        cur_rev_found = False

        for script in revisions:
            if script.revision in rev:
                cur_rev_found = True
            print(
                (
                    "{}  {} {} → {}: {}".format(
                        "▶" if script.revision in rev else " ",
                        "♦" if script.is_head else " ",
                        script.down_revision,
                        script.revision,
                        script.doc,
                    )
                )
            )
        if not cur_rev_found:
            logger.warning(f"🔴 Current rev {rev} cannot be found in revisions history.")
        return []

    pkg_env.run_env(print_list)


def fetch_command(pkg, revision=None):
    """
    fetch a revision without migrating
    """

    def do_stamp(rev, context, revision=revision):
        context.stamp(context.script, revision)
        mark_changed(DBSESSION())
        return []

    PackageEnvironment(pkg).run_env(do_stamp)


def fetch_head_command(pkg="caerp"):
    """
    fetch the latest revision
    """
    pkg_env = PackageEnvironment(pkg)
    revision = pkg_env.script_dir.get_current_head()
    fetch_command(pkg, revision)


def is_alembic_initialized(pkg="caerp") -> bool:
    pkg_env = PackageEnvironment(pkg)
    session = DBSESSION()
    try:
        revision = session.execute(f"SELECT * from {pkg_env.version_table}").scalar()
    except DatabaseError as e:
        # alembic table does not exist
        return False
    return bool(revision)


def revision_command(pkg, message, empty=False):
    command_args = dict(
        message=message,
        autogenerate=True,
        sql=False,
        head="head",
        splice=False,
        branch_label=None,
        version_path=None,
        rev_id=None,
        depends_on=None,
    )
    env = PackageEnvironment(pkg)

    revision_context = autogen.RevisionContext(
        env.config,
        env.script_dir,
        command_args,
    )

    def get_rev(rev, context):
        # autogen._produce_migration_diffs(context, template_args, imports)
        if not empty:
            revision_context.run_autogenerate(rev, context)
        return []

    revision_context.template_args["caerp_version"] = caerp_version()
    env.run_env(
        get_rev,
        as_sql=False,
        revision_context=revision_context,
        template_args=revision_context.template_args,
    )
    scripts = [script for script in revision_context.generate_scripts()]
    return scripts


def rebase_command(pkg, first_rev_id, second_rev_id, merge_rev_id=None):
    env = PackageEnvironment(pkg)

    try:
        first_rev = env.script_dir.get_revision(first_rev_id)
        second_rev = env.script_dir.get_revision(second_rev_id)
        if merge_rev_id:
            merge_rev = env.script_dir.get_revision(merge_rev_id)
        else:
            merge_rev = None
    except ValueError as e:
        logger.error(e)
        return

    if second_rev.is_merge_point:
        logger.error(
            "Second revision cannot be a merge revision :"
            " please rebase manually or swap rev1 / rev2 args."
        )

    if merge_rev:
        if set(merge_rev.down_revision) != {first_rev_id, second_rev_id}:
            logger.error(
                f"{first_rev_id} and {second_rev_id} are not merged by {merge_rev_id}."
            )
            return

    else:
        if not first_rev.is_head or not second_rev.is_head:
            logger.error(f"{first_rev_id} and {second_rev_id} are not diverging heads")
            return

    logger.info(
        f"Rebasing :  {first_rev.revision} branch first, {second_rev.revision} branch then"
    )
    second_branch_start, common_ancestor_id = _get_fork_start(
        env, second_rev_id, first_rev_id
    )
    _amend_down_revision(second_branch_start, common_ancestor_id, first_rev_id)
    if merge_rev:
        logger.info(f"Deleting {merge_rev.path}")
        os.remove(merge_rev.path)

        # If the deleted merge revision is not a head, remove it from revision chains
        revisions = list(env.script_dir.walk_revisions())
        for rev in revisions:
            down_revs = util.to_tuple(rev.down_revision) or tuple()
            if merge_rev_id in down_revs:
                logger.info(
                    f"Unplugging deleted merge rev {merge_rev_id} from {rev.revision}"
                )
                _amend_down_revision(rev, merge_rev_id, second_rev_id)


def _amend_down_revision(
    rev_to_amend: Script, old_down_rev_id: str, new_down_rev_id: str
):
    """
    Amend the script of the rev_to_amend inplace to change its down revision.

    It does alter the revision .py file (inplace edit)
    """
    original_code = open(rev_to_amend.path).read()
    patched_code = original_code.replace(old_down_rev_id, new_down_rev_id)
    with open(rev_to_amend.path, "w") as f:
        f.write(patched_code)


def merge_command(pkg, rev1=None, rev2=None):
    if (rev1 and not rev2) or (rev2 and not rev1):
        logger.error("Either specify --rev1 and --rev2 or None of them")
        return

    env = PackageEnvironment(pkg)

    if rev1 and rev2:
        heads = [rev1, rev2]
    else:
        heads = []

        def get_heads(rev, context):
            for i in context.script.get_heads():
                heads.append(i)
            return []

        env.run_env(get_heads)

    if len(heads) > 1:

        def create_merge_revision(rev, context):
            context.script.generate_revision(
                revid=rev_id(),
                message="Revision merge",
                refresh=True,
                head=heads,
                # template-only arg:
                caerp_version=caerp_version(),
            )
            return []

        env.run_env(create_merge_revision)

    else:
        logger.error(
            "There is nothing to merge (only one head : {}), aborting".format(heads[0])
        )


def migrate_entry_point():
    """Migrate MoOGLi's database
    Usage:
        migrate <config_uri> list [--pkg=<pkg>]
        migrate <config_uri> upgrade [--rev=<rev>] [--pkg=<pkg>]
        migrate <config_uri> fetch [--rev=<rev>] [--pkg=<pkg>]
        migrate <config_uri> revision [--m=<message>] [--empty] [--pkg=<pkg>]
        migrate <config_uri> downgrade [--rev=<rev>] [--pkg=<pkg>]
        migrate <config_uri> merge [--rev1=<rev>] [--rev2=<rev>] [--pkg=<pkg>]
        migrate <config_uri> rebase --rev1=<rev> --rev2=<rev> [--revmerge=<rev>] [--pkg=<pkg>]

    o list : all the revisions
    o upgrade : upgrade the app to the latest revision
    o revision : create a migration file with the given message (trying to detect changes, unless --empty is used)
    o fetch : set the revision
    o downgrade : downgrade the database
    o merge : create a merge revision between two diverging revisions (you might ommit --rev*, they will get autodected)
    o rebase : linearize two diverging branches by putting <rev1> branch before and <rev2> branch (order matters). Optionally replacing a merge revision (the command will delete it).

    Options:
        -h --help     Show this screen.
    """

    def callback(arguments, env):
        from caerp.utils.sys_environment import package_name

        args = (get_value(arguments, "pkg", package_name),)
        if arguments["list"]:
            func = list_command
        elif arguments["upgrade"]:
            args += (arguments["--rev"],)
            func = upgrade_command
        elif arguments["fetch"]:
            args += (arguments["--rev"],)
            func = fetch_command
        elif arguments["revision"]:
            args += (arguments["--m"], arguments["--empty"])
            func = revision_command
        elif arguments["downgrade"]:
            args += (arguments["--rev"],)
            func = downgrade_command
        elif arguments["merge"]:
            args += (arguments["--rev1"], arguments["--rev2"])
            func = merge_command
        elif arguments["rebase"]:
            args += (arguments["--rev1"], arguments["--rev2"], arguments["--revmerge"])
            func = rebase_command
        return func(*args)

    try:
        return command(callback, migrate_entry_point.__doc__)
    except CommandError as e:
        if "has multiple heads" in str(e):
            print(MULTIPLE_HEADS_MSG)
            exit(1)
        else:
            raise
