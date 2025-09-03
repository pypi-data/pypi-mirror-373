from alembic import context
import traceback
import transaction

from caerp.alembic.exceptions import MigrationError, RollbackError
from caerp_base.models.base import DBSESSION
from caerp.models import DBBASE
from caerp.models.config import Config


def run_migrations_online():
    bind = DBSESSION.get_bind(Config)
    if bind is None:
        raise ValueError(
            "\nYou must do MoOGLi migrations using the 'caerp-migrate' script"
            "\nand not through 'alembic' directly."
        )

    transaction.begin()
    connection = DBSESSION.connection(mapper=Config)

    context.configure(
        connection=connection,
        target_metadata=DBBASE.metadata,
        compare_type=True,
    )

    try:
        context.run_migrations()
    except Exception as migration_e:
        traceback.print_exc()
        try:
            transaction.abort()
        except Exception as rollback_e:
            traceback.print_exc()
            raise RollbackError(rollback_e)
        else:
            raise MigrationError(migration_e)
    else:
        transaction.commit()
    finally:
        # connection.close()
        pass


run_migrations_online()
