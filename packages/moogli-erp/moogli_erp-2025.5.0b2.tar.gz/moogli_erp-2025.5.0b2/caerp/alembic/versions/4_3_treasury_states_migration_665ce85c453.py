# -*-coding:utf-8-*-
"""4.3 Treasury states migration

Revision ID: 665ce85c453
Revises: 432e6cd0752c
Create Date: 2019-02-11 19:58:39.468639

"""

# revision identifiers, used by Alembic.
revision = "665ce85c453"
down_revision = "2a7da76844bd"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def insert_measure_base_tables():
    """
    Insert a new base table for all accounting measures models
    """
    conn = op.get_bind()
    base_category_helper = sa.Table(
        "base_accounting_measure_type_category",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type_", sa.String(30)),
        sa.Column("label", sa.String(255)),
        sa.Column("active", sa.Boolean()),
        sa.Column("order", sa.Integer),
    )
    base_type_helper = sa.Table(
        "base_accounting_measure_type",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type_", sa.String(30)),
        sa.Column("category_id", sa.Integer),
        sa.Column("label", sa.String(255)),
        sa.Column("account_prefix", sa.String(255)),
        sa.Column("active", sa.Boolean()),
        sa.Column("order", sa.Integer),
        sa.Column("is_total", sa.Boolean()),
        sa.Column("total_type", sa.String(20)),
    )
    base_grid_helper = sa.Table(
        "base_accounting_measure_grid",
        sa.MetaData(),
        sa.Column("type_", sa.String(30)),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("datetime", sa.DateTime()),
        sa.Column("company_id", sa.Integer),
        sa.Column("upload_id", sa.Integer),
    )
    base_measure_helper = sa.Table(
        "base_accounting_measure",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type_", sa.String(30)),
        sa.Column("label", sa.String(255)),
        sa.Column("value", sa.Float()),
        sa.Column("grid_id", sa.Integer),
        sa.Column("order", sa.Integer),
        sa.Column("measure_type_id", sa.Integer),
    )

    # IncomeStatements
    category_helper = sa.Table(
        "income_statement_measure_type_category",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("label", sa.String(255)),
        sa.Column("active", sa.Boolean()),
        sa.Column("order", sa.Integer),
    )
    for category in conn.execute(category_helper.select()):
        conn.execute(
            base_category_helper.insert().values(
                id=category.id,
                label=category.label,
                active=category.active,
                order=category.order,
                type_="income_statement",
            )
        )
    type_helper = sa.Table(
        "income_statement_measure_type",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("category_id", sa.Integer),
        sa.Column("label", sa.String(255)),
        sa.Column("account_prefix", sa.String(255)),
        sa.Column("active", sa.Boolean()),
        sa.Column("order", sa.Integer),
        sa.Column("is_total", sa.Boolean()),
        sa.Column("total_type", sa.String(20)),
    )
    # Used to store orders by id
    income_statement_measure_type_orders = {}

    for typ in conn.execute(type_helper.select()):
        income_statement_measure_type_orders[typ.id] = typ.order

        conn.execute(
            base_type_helper.insert().values(
                id=typ.id,
                category_id=typ.category_id,
                label=typ.label,
                active=typ.active,
                account_prefix=typ.account_prefix,
                order=typ.order,
                is_total=typ.is_total,
                total_type=typ.total_type,
                type_="income_statement",
            )
        )

    grid_helper = sa.Table(
        "income_statement_measure_grid",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("datetime", sa.DateTime()),
        sa.Column("company_id", sa.Integer),
        sa.Column("upload_id", sa.Integer),
    )
    for grid in conn.execute(grid_helper.select()):
        conn.execute(
            base_grid_helper.insert().values(
                id=grid.id,
                datetime=grid.datetime,
                company_id=grid.company_id,
                upload_id=grid.upload_id,
                type_="income_statement",
            )
        )

    measure_helper = sa.Table(
        "income_statement_measure",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("label", sa.String(255)),
        sa.Column("value", sa.Float()),
        sa.Column("grid_id", sa.Integer),
        sa.Column("measure_type_id", sa.Integer),
    )
    for measure in conn.execute(measure_helper.select()):
        if measure.measure_type_id is not None:
            conn.execute(
                base_measure_helper.insert().values(
                    id=measure.id,
                    type_="income_statement",
                    label=measure.label,
                    value=measure.value,
                    grid_id=measure.grid_id,
                    measure_type_id=measure.measure_type_id,
                    order=income_statement_measure_type_orders[measure.measure_type_id],
                )
            )
        else:
            conn.execute(
                measure_helper.delete().where(measure_helper.c.id == measure.id)
            )

    # Treasury Measures Migration
    category_helper = sa.Table(
        "treasury_measure_type_category",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
    )
    category_ids = {}
    for index, label in enumerate(("Référence", "Future", "Autres")):
        req = conn.execute(
            base_category_helper.insert().values(
                type_="treasury", label=label, active=True, order=index
            )
        )
        id_ = req.inserted_primary_key[0]
        conn.execute(category_helper.insert().values(id=id_))
        category_ids[index] = id_

    type_helper = sa.Table(
        "treasury_measure_type",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("internal_id", sa.Integer),
        sa.Column("label", sa.String(255)),
        sa.Column("account_prefix", sa.String(255)),
        sa.Column("active", sa.Boolean()),
    )
    measure_helper = sa.Table(
        "treasury_measure",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("measure_type_id", sa.Integer),
        sa.Column("label", sa.String(255)),
        sa.Column("grid_id", sa.Integer),
        sa.Column("value", sa.Float()),
    )
    grid_helper = sa.Table(
        "treasury_measure_grid",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("datetime", sa.DateTime()),
        sa.Column("company_id", sa.Integer),
        sa.Column("upload_id", sa.Integer),
    )
    grid_id_mapper = {}
    for grid in conn.execute(grid_helper.select()):
        old_id = grid.id
        req = conn.execute(
            base_grid_helper.insert().values(
                datetime=grid.datetime,
                company_id=grid.company_id,
                upload_id=grid.upload_id,
                type_="treasury",
            )
        )
        new_id = req.inserted_primary_key[0]
        conn.execute(
            grid_helper.update().where(grid_helper.c.id == old_id).values(id=new_id)
        )
        grid_id_mapper[old_id] = new_id

    measure_type_id_mapper = {}
    # internal_id -> category index
    type_category_index = {1: 0, 2: 0, 3: 0, 5: 1, 6: 1, 7: 1, 9: 2}
    orders = {1: 0, 2: 1, 3: 2, 5: 4, 6: 5, 7: 6, 9: 8}

    config_helper = sa.Table(
        "config",
        sa.MetaData(),
        sa.Column("config_name", sa.String(255), primary_key=True),
        sa.Column("config_value", sa.Text()),
    )

    treasury_measure_ui = conn.execute(
        config_helper.select().where(
            config_helper.c.config_name == "treasury_measure_ui"
        )
    ).first()

    if treasury_measure_ui is not None:
        highlight_internal_id = int(treasury_measure_ui.config_value)
    else:
        # The default one
        highlight_internal_id = 1

    # Stocke les ordres des types de mesures par id
    treasury_measure_type_orders = {}

    for item in conn.execute(type_helper.select()):
        # on recup les types confiurés, on les reconstruit dans le nouveau type
        # de données
        old_id = item.id
        # On récupère l'id de catégorie
        category_id = category_ids[type_category_index[item.internal_id]]

        if item.internal_id == 1:
            is_total = True
            total_type = "account_prefix"
        else:
            is_total = False
            total_type = None

        req = conn.execute(
            base_type_helper.insert().values(
                type_="treasury",
                label=item.label,
                account_prefix=item.account_prefix,
                active=item.active,
                category_id=category_id,
                is_total=is_total,
                total_type=total_type,
                order=orders[item.internal_id],
            )
        )
        new_id = req.inserted_primary_key[0]
        conn.execute(
            type_helper.update().where(type_helper.c.id == item.id).values(id=new_id)
        )
        treasury_measure_type_orders[new_id] = orders[item.internal_id]

        if item.internal_id == highlight_internal_id:
            conn.execute(
                config_helper.update()
                .where(config_helper.c.config_name == "treasury_measure_ui")
                .values(config_value=new_id)
            )

        measure_type_id_mapper[old_id] = new_id

    for entry in (
        dict(
            label="Trésorerie de référence",
            is_total=True,
            account_prefix="Référence",
            total_type="categories",
            order=3,
            active=True,
            category_id=category_ids[0],
        ),
        dict(
            label="Trésorerie future",
            is_total=True,
            account_prefix="{Référence}+{Future}",
            total_type="complex_total",
            order=7,
            active=True,
            category_id=category_ids[1],
        ),
        dict(
            label="Résultat de l'enseigne",
            is_total=True,
            account_prefix="{Référence}+{Future}+{Autres}",
            total_type="complex_total",
            order=9,
            active=True,
            category_id=category_ids[2],
        ),
    ):
        req = conn.execute(base_type_helper.insert().values(type_="treasury", **entry))
        new_id = req.inserted_primary_key[0]
        conn.execute(type_helper.insert().values(id=new_id))
        treasury_measure_type_orders[new_id] = entry["order"]
        if entry["order"] + 1 == highlight_internal_id:
            conn.execute(
                config_helper.update()
                .where(config_helper.c.config_name == "treasury_measure_ui")
                .values(config_value=new_id)
            )

    for measure in conn.execute(measure_helper.select()):
        measure_type_id = measure_type_id_mapper[measure.measure_type_id]
        req = conn.execute(
            base_measure_helper.insert().values(
                type_="treasury",
                label=measure.label,
                value=measure.value,
                grid_id=grid_id_mapper[measure.grid_id],
                measure_type_id=measure_type_id,
                order=treasury_measure_type_orders[measure_type_id],
            )
        )
        new_id = req.inserted_primary_key[0]
        conn.execute(
            measure_helper.update()
            .where(measure_helper.c.id == measure.id)
            .values(id=new_id)
        )


def insert_computed_measure_in_income_statement_grids(session):
    # Pour chaque grille :
    #    - on va récolter les computation_values
    #    - pour chaque measure_type complexe
    #    - on va créer une mesure avec la computation value qui va bien
    from caerp.models.accounting.income_statement_measures import (
        IncomeStatementMeasureType,
        IncomeStatementMeasureTypeCategory,
        IncomeStatementMeasureGrid,
        IncomeStatementMeasure,
    )

    active_types_query = (
        IncomeStatementMeasureType.query()
        .join(IncomeStatementMeasureTypeCategory)
        .filter(IncomeStatementMeasureType.active == True)
        .filter(IncomeStatementMeasureTypeCategory.active == True)
    )

    common_types = active_types_query.filter(
        sa.or_(
            IncomeStatementMeasureType.is_total == False,
            IncomeStatementMeasureType.total_type == "account_prefix",
        )
    )

    computed_types = (
        active_types_query.filter(IncomeStatementMeasureType.is_total == True)
        .filter(IncomeStatementMeasureType.total_type != "account_prefix")
        .all()
    )

    for grid in IncomeStatementMeasureGrid.query():
        data = {}
        for measure in grid.measures:
            data[measure.measure_type.label] = measure.value
            if measure.measure_type.category.label not in data:
                data[measure.measure_type.category.label] = 0
            data[measure.measure_type.category.label] += measure.value

        grid_types = IncomeStatementMeasure.get_measure_types(grid.id)
        if grid_types:
            for measure_type in common_types:
                if measure_type not in grid_types:
                    item = IncomeStatementMeasure(
                        label=measure_type.label,
                        order=measure_type.order,
                        measure_type_id=measure_type.id,
                        grid_id=grid.id,
                    )
                    session.add(item)

        for measure_type in computed_types:
            item = IncomeStatementMeasure(
                value=measure_type.compute_total(data),
                label=measure_type.label,
                grid_id=grid.id,
                measure_type_id=measure_type.id,
                order=measure_type.order,
            )
            session.add(item)
            data[measure_type.label] = item.value


def insert_computed_measure_in_treasury_grids(session):
    # Pour chaque grille :
    #    - on va récolter les computation_values
    #    - pour chaque measure_type complexe
    #    - on va créer une mesure avec la computation value qui va bien
    from caerp.models.accounting.treasury_measures import (
        TreasuryMeasureType,
        TreasuryMeasureTypeCategory,
        TreasuryMeasureGrid,
        TreasuryMeasure,
    )

    active_types_query = (
        TreasuryMeasureType.query()
        .join(TreasuryMeasureTypeCategory)
        .filter(TreasuryMeasureType.active == True)
        .filter(TreasuryMeasureTypeCategory.active == True)
    )

    common_types = active_types_query.filter(
        sa.or_(
            TreasuryMeasureType.is_total == False,
            TreasuryMeasureType.total_type == "account_prefix",
        )
    )

    computed_types = (
        active_types_query.filter(TreasuryMeasureType.is_total == True)
        .filter(TreasuryMeasureType.total_type != "account_prefix")
        .all()
    )

    for grid in TreasuryMeasureGrid.query():
        data = {}
        for measure in grid.measures:
            data[measure.measure_type.label] = measure.value
            if measure.measure_type.category.label not in data:
                data[measure.measure_type.category.label] = 0
            data[measure.measure_type.category.label] += measure.value

        grid_types = TreasuryMeasure.get_measure_types(grid.id)
        if grid_types:
            for measure_type in common_types:
                if measure_type not in grid_types:
                    item = TreasuryMeasure(
                        label=measure_type.label,
                        order=measure_type.order,
                        measure_type_id=measure_type.id,
                        grid_id=grid.id,
                    )
                    session.add(item)

        for measure_type in computed_types:
            item = TreasuryMeasure(
                value=measure_type.compute_total(data),
                label=measure_type.label,
                grid_id=grid.id,
                measure_type_id=measure_type.id,
                order=measure_type.order,
            )
            session.add(item)
            data[measure_type.label] = item.value


def update_database_structure():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "fk_income_statement_measure_measure_type_id",
        "income_statement_measure",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_income_statement_measure_grid_id",
        "income_statement_measure",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_income_statement_measure_grid_company_id",
        "income_statement_measure_grid",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_income_statement_measure_grid_upload_id",
        "income_statement_measure_grid",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_income_statement_measure_type_category_id",
        "income_statement_measure_type",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_treasury_measure_grid_id", "treasury_measure", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_treasury_measure_measure_type_id", "treasury_measure", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_treasury_measure_grid_upload_id",
        "treasury_measure_grid",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_treasury_measure_grid_company_id",
        "treasury_measure_grid",
        type_="foreignkey",
    )

    op.add_column("accounting_operation_upload", sa.Column("updated_at", sa.DateTime))
    op.execute(
        "update accounting_operation_upload set updated_at=created_at where filetype IN ('general_ledger', 'analytical_balance');"
    )
    op.execute(
        "update accounting_operation_upload set updated_at=date where filetype = 'synchronized_accounting'"
    )
    op.execute(
        "update accounting_operation_upload set date=created_at where filetype ='synchronized_accounting';"
    )
    op.execute(
        "update accounting_operation_upload set created_at=updated_at where filetype ='synchronized_accounting';"
    )
    insert_measure_base_tables()

    op.create_foreign_key(
        op.f("fk_income_statement_measure_id"),
        "income_statement_measure",
        "base_accounting_measure",
        ["id"],
        ["id"],
    )
    op.drop_column("income_statement_measure", "grid_id")
    op.drop_column("income_statement_measure", "measure_type_id")
    op.drop_column("income_statement_measure", "value")
    op.drop_column("income_statement_measure", "label")
    op.create_foreign_key(
        op.f("fk_income_statement_measure_grid_id"),
        "income_statement_measure_grid",
        "base_accounting_measure_grid",
        ["id"],
        ["id"],
    )
    op.drop_column("income_statement_measure_grid", "upload_id")
    op.drop_column("income_statement_measure_grid", "company_id")
    op.drop_column("income_statement_measure_grid", "datetime")
    op.create_foreign_key(
        op.f("fk_income_statement_measure_type_id"),
        "income_statement_measure_type",
        "base_accounting_measure_type",
        ["id"],
        ["id"],
    )
    op.drop_column("income_statement_measure_type", "account_prefix")
    op.drop_column("income_statement_measure_type", "is_total")
    op.drop_column("income_statement_measure_type", "label")
    op.drop_column("income_statement_measure_type", "total_type")
    op.drop_column("income_statement_measure_type", "active")
    op.drop_column("income_statement_measure_type", "category_id")
    op.drop_column("income_statement_measure_type", "order")
    op.create_foreign_key(
        op.f("fk_income_statement_measure_type_category_id"),
        "income_statement_measure_type_category",
        "base_accounting_measure_type_category",
        ["id"],
        ["id"],
    )
    op.drop_column("income_statement_measure_type_category", "active")
    op.drop_column("income_statement_measure_type_category", "order")
    op.drop_column("income_statement_measure_type_category", "label")

    op.create_foreign_key(
        op.f("fk_treasury_measure_id"),
        "treasury_measure",
        "base_accounting_measure",
        ["id"],
        ["id"],
    )
    op.drop_column("treasury_measure", "grid_id")
    op.drop_column("treasury_measure", "measure_type_id")
    op.drop_column("treasury_measure", "value")
    op.drop_column("treasury_measure", "label")
    op.create_foreign_key(
        op.f("fk_treasury_measure_grid_id"),
        "treasury_measure_grid",
        "base_accounting_measure_grid",
        ["id"],
        ["id"],
    )
    op.drop_column("treasury_measure_grid", "upload_id")
    op.drop_column("treasury_measure_grid", "company_id")
    op.drop_column("treasury_measure_grid", "datetime")
    op.create_foreign_key(
        op.f("fk_treasury_measure_type_id"),
        "treasury_measure_type",
        "base_accounting_measure_type",
        ["id"],
        ["id"],
    )
    op.drop_column("treasury_measure_type", "active")
    op.drop_column("treasury_measure_type", "account_prefix")
    op.drop_column("treasury_measure_type", "internal_id")
    op.drop_column("treasury_measure_type", "label")
    ### end Alembic commands ###


def migrate_datas():
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    insert_computed_measure_in_income_statement_grids(session)
    insert_computed_measure_in_treasury_grids(session)


def upgrade():
    update_database_structure()
    migrate_datas()


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "workshop_action",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.add_column(
        "workshop", sa.Column("info2", mysql.VARCHAR(length=125), nullable=True)
    )
    op.add_column(
        "workshop", sa.Column("info3", mysql.VARCHAR(length=125), nullable=True)
    )
    op.add_column(
        "workshop", sa.Column("info1", mysql.VARCHAR(length=125), nullable=True)
    )
    op.alter_column(
        "userdatas_socialdocs",
        "status",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.add_column(
        "user_datas", sa.Column("parcours_last_avenant", sa.DATE(), nullable=True)
    )
    op.add_column(
        "user_datas",
        sa.Column("situation_situation", mysql.VARCHAR(length=20), nullable=True),
    )
    op.add_column(
        "user_datas", sa.Column("parcours_start_date", sa.DATE(), nullable=True)
    )
    op.add_column(
        "user_datas",
        sa.Column("parcours_contract_type", mysql.VARCHAR(length=4), nullable=True),
    )
    op.add_column(
        "user_datas", sa.Column("parcours_taux_horaire", mysql.FLOAT(), nullable=True)
    )
    op.add_column("user_datas", sa.Column("sortie_date", sa.DATE(), nullable=True))
    op.add_column(
        "user_datas",
        sa.Column(
            "parcours_employee_quality_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "user_datas",
        sa.Column("parcours_salary_letters", mysql.VARCHAR(length=100), nullable=True),
    )
    op.add_column(
        "user_datas", sa.Column("parcours_num_hours", mysql.FLOAT(), nullable=True)
    )
    op.add_column(
        "user_datas", sa.Column("parcours_end_date", sa.DATE(), nullable=True)
    )
    op.add_column(
        "user_datas",
        sa.Column(
            "parcours_taux_horaire_letters", mysql.VARCHAR(length=250), nullable=True
        ),
    )
    op.add_column(
        "user_datas", sa.Column("parcours_salary", mysql.FLOAT(), nullable=True)
    )
    op.drop_constraint(op.f("fk_user_datas_id"), "user_datas", type_="foreignkey")
    op.create_index(
        "fk_user_datas_parcours_employee_quality_id",
        "user_datas",
        ["parcours_employee_quality_id"],
        unique=False,
    )
    op.alter_column(
        "tva", "name", existing_type=mysql.VARCHAR(length=15), nullable=True
    )
    op.alter_column(
        "tva",
        "default",
        existing_type=sa.Boolean(),
        type_=mysql.INTEGER(display_width=11),
        existing_nullable=True,
    )
    op.alter_column(
        "tva",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.add_column(
        "treasury_measure_type",
        sa.Column("label", mysql.VARCHAR(length=255), nullable=True),
    )
    op.add_column(
        "treasury_measure_type",
        sa.Column(
            "internal_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "treasury_measure_type",
        sa.Column("account_prefix", mysql.VARCHAR(length=255), nullable=True),
    )
    op.add_column(
        "treasury_measure_type",
        sa.Column(
            "active", mysql.TINYINT(display_width=1), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint(
        op.f("fk_treasury_measure_type_id"), "treasury_measure_type", type_="foreignkey"
    )
    op.add_column(
        "treasury_measure_grid", sa.Column("datetime", mysql.DATETIME(), nullable=True)
    )
    op.add_column(
        "treasury_measure_grid",
        sa.Column(
            "company_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "treasury_measure_grid",
        sa.Column(
            "upload_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_constraint(
        op.f("fk_treasury_measure_grid_id"), "treasury_measure_grid", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_treasury_measure_grid_company_id",
        "treasury_measure_grid",
        "company",
        ["company_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_treasury_measure_grid_upload_id",
        "treasury_measure_grid",
        "accounting_operation_upload",
        ["upload_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.add_column(
        "treasury_measure", sa.Column("label", mysql.VARCHAR(length=255), nullable=True)
    )
    op.add_column("treasury_measure", sa.Column("value", mysql.FLOAT(), nullable=True))
    op.add_column(
        "treasury_measure",
        sa.Column(
            "measure_type_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "treasury_measure",
        sa.Column(
            "grid_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_constraint(
        op.f("fk_treasury_measure_id"), "treasury_measure", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_treasury_measure_measure_type_id",
        "treasury_measure",
        "treasury_measure_type",
        ["measure_type_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_treasury_measure_grid_id",
        "treasury_measure",
        "treasury_measure_grid",
        ["grid_id"],
        ["id"],
    )
    op.alter_column(
        "trainer_datas",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "templates",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.drop_constraint(
        op.f("fk_task_status_status_person_id"), "task_status", type_="foreignkey"
    )
    op.create_index("statusPerson", "task_status", ["status_person_id"], unique=False)
    op.alter_column(
        "task_status",
        "status_person_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
    op.alter_column(
        "task_status", "status_comment", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "task_status",
        "status_code",
        existing_type=mysql.VARCHAR(length=10),
        nullable=False,
    )
    op.add_column(
        "task",
        sa.Column(
            "version",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_constraint(op.f("fk_task_owner_id"), "task", type_="foreignkey")
    op.drop_constraint(op.f("fk_task_id"), "task", type_="foreignkey")
    op.drop_constraint(op.f("fk_task_phase_id"), "task", type_="foreignkey")
    op.drop_constraint(op.f("fk_task_status_person_id"), "task", type_="foreignkey")
    op.create_index("statusPerson", "task", ["status_person_id"], unique=False)
    op.alter_column(
        "task",
        "status_person_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
    op.alter_column(
        "task", "status_comment", existing_type=mysql.TEXT(), nullable=False
    )
    op.alter_column(
        "task", "status", existing_type=mysql.VARCHAR(length=10), nullable=False
    )
    op.alter_column(
        "task",
        "round_floor",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "task",
        "legacy_number",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=False,
    )
    op.alter_column(
        "statistic_sheet",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "sale_training_group",
        "modality_two",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "sale_training_group",
        "modality_one",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "sale_file_requirement",
        "validation",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "project_type",
        "default",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.create_index("client_id", "project_customer", ["customer_id"], unique=False)
    op.alter_column(
        "project_customer",
        "customer_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
    op.drop_constraint(op.f("fk_project_id"), "project", type_="foreignkey")
    op.alter_column(
        "project",
        "archived",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "product",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "payment_conditions",
        "default",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.drop_constraint(op.f("fk_payment_bank_id"), "payment", type_="foreignkey")
    op.alter_column(
        "payment",
        "exported",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "payment",
        "bank_remittance_id",
        existing_type=mysql.VARCHAR(length=255),
        nullable=False,
    )
    op.alter_column(
        "oidc_token",
        "revoked",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "oidc_id_token",
        "revoked",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "oidc_code",
        "revoked",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "oidc_client",
        "revoked",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "login",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.drop_constraint(op.f("fk_invoice_estimation_id"), "invoice", type_="foreignkey")
    op.alter_column(
        "invoice",
        "financial_year",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
    op.alter_column(
        "invoice",
        "exported",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "indicator",
        "forced",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.add_column(
        "income_statement_measure_type_category",
        sa.Column("label", mysql.VARCHAR(length=255), nullable=False),
    )
    op.add_column(
        "income_statement_measure_type_category",
        sa.Column(
            "order", mysql.INTEGER(display_width=11), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "income_statement_measure_type_category",
        sa.Column(
            "active", mysql.TINYINT(display_width=1), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint(
        op.f("fk_income_statement_measure_type_category_id"),
        "income_statement_measure_type_category",
        type_="foreignkey",
    )
    op.add_column(
        "income_statement_measure_type",
        sa.Column(
            "order", mysql.INTEGER(display_width=11), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "income_statement_measure_type",
        sa.Column(
            "category_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "income_statement_measure_type",
        sa.Column(
            "active", mysql.TINYINT(display_width=1), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "income_statement_measure_type",
        sa.Column("total_type", mysql.VARCHAR(length=20), nullable=True),
    )
    op.add_column(
        "income_statement_measure_type",
        sa.Column("label", mysql.VARCHAR(length=255), nullable=False),
    )
    op.add_column(
        "income_statement_measure_type",
        sa.Column(
            "is_total",
            mysql.TINYINT(display_width=1),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "income_statement_measure_type",
        sa.Column("account_prefix", mysql.VARCHAR(length=255), nullable=True),
    )
    op.drop_constraint(
        op.f("fk_income_statement_measure_type_id"),
        "income_statement_measure_type",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_income_statement_measure_type_category_id",
        "income_statement_measure_type",
        "income_statement_measure_type_category",
        ["category_id"],
        ["id"],
    )
    op.add_column(
        "income_statement_measure_grid",
        sa.Column("datetime", mysql.DATETIME(), nullable=True),
    )
    op.add_column(
        "income_statement_measure_grid",
        sa.Column(
            "company_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "income_statement_measure_grid",
        sa.Column(
            "upload_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_constraint(
        op.f("fk_income_statement_measure_grid_id"),
        "income_statement_measure_grid",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_income_statement_measure_grid_upload_id",
        "income_statement_measure_grid",
        "accounting_operation_upload",
        ["upload_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_income_statement_measure_grid_company_id",
        "income_statement_measure_grid",
        "company",
        ["company_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.add_column(
        "income_statement_measure",
        sa.Column("label", mysql.VARCHAR(length=255), nullable=True),
    )
    op.add_column(
        "income_statement_measure", sa.Column("value", mysql.FLOAT(), nullable=True)
    )
    op.add_column(
        "income_statement_measure",
        sa.Column(
            "measure_type_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "income_statement_measure",
        sa.Column(
            "grid_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_constraint(
        op.f("fk_income_statement_measure_id"),
        "income_statement_measure",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_income_statement_measure_grid_id",
        "income_statement_measure",
        "income_statement_measure_grid",
        ["grid_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_income_statement_measure_measure_type_id",
        "income_statement_measure",
        "income_statement_measure_type",
        ["measure_type_id"],
        ["id"],
    )
    op.alter_column(
        "groups",
        "primary",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "groups", "label", existing_type=mysql.VARCHAR(length=255), nullable=True
    )
    op.alter_column(
        "groups",
        "editable",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "external_activity_datas",
        "employer_visited",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "expensetel_type",
        "percentage",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=True,
    )
    op.alter_column(
        "expensetel_type",
        "initialize",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "expensekm_type",
        "amount",
        existing_type=sa.Float(precision=4),
        type_=mysql.FLOAT(),
        nullable=True,
    )
    op.alter_column(
        "expense_type", "label", existing_type=mysql.VARCHAR(length=50), nullable=True
    )
    op.alter_column(
        "expense_type",
        "contribution",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "expense_type", "code", existing_type=mysql.VARCHAR(length=15), nullable=True
    )
    op.alter_column(
        "expense_type",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
        existing_server_default=sa.text("1"),
    )
    op.drop_constraint(op.f("fk_expense_sheet_id"), "expense_sheet", type_="foreignkey")
    op.alter_column(
        "expense_sheet",
        "purchase_exported",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "expense_sheet",
        "justified",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "expense_sheet",
        "expense_exported",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "expense_payment",
        "waiver",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "expense_payment",
        "exported",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "estimation",
        "geninv",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column("customer", "updated_at", existing_type=sa.DATE(), nullable=True)
    op.alter_column(
        "customer",
        "registration",
        existing_type=sa.String(length=255),
        type_=mysql.VARCHAR(length=50),
        existing_nullable=True,
    )
    op.alter_column(
        "customer", "name", existing_type=mysql.VARCHAR(length=255), nullable=False
    )
    op.alter_column("customer", "created_at", existing_type=sa.DATE(), nullable=True)
    op.alter_column(
        "customer",
        "company_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=True,
    )
    op.alter_column(
        "customer",
        "archived",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
        existing_server_default=sa.text("0"),
    )
    op.alter_column(
        "custom_invoice_book_entry_module",
        "enabled",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "custom_invoice_book_entry_module",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "configurable_option",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.create_index("key", "config_files", ["key"], unique=True)
    op.drop_constraint(op.f("uq_config_files_key"), "config_files", type_="unique")
    op.add_column(
        "company", sa.Column("old_active", mysql.VARCHAR(length=1), nullable=True)
    )
    op.alter_column("company", "updated_at", existing_type=sa.DATE(), nullable=True)
    op.alter_column("company", "created_at", existing_type=sa.DATE(), nullable=True)
    op.alter_column(
        "company",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "career_stage",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.drop_constraint(
        op.f("fk_cancelinvoice_invoice_id"), "cancelinvoice", type_="foreignkey"
    )
    op.alter_column(
        "cancelinvoice",
        "financial_year",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
    op.alter_column(
        "cancelinvoice",
        "exported",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "cae_situation_option",
        "is_integration",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "business_type_task_mention",
        "mandatory",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "business_type_file_type",
        "validation",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "business_payment_deadline",
        "invoiced",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "business_payment_deadline",
        "deposit",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "business",
        "closed",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "baseexpense_line",
        "valid",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "base_project_type",
        "private",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "base_project_type",
        "editable",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "base_project_type",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "base_accounting_measure_type_category",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "base_accounting_measure_type",
        "is_total",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "base_accounting_measure_type",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "base_accounting_measure",
        "value",
        existing_type=sa.Float(precision=2),
        type_=mysql.FLOAT(),
        existing_nullable=True,
    )
    op.alter_column(
        "bank_account",
        "default",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "activity_type",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "activity_action",
        "active",
        existing_type=sa.Boolean(),
        type_=mysql.TINYINT(display_width=1),
        existing_nullable=True,
    )
    op.alter_column(
        "accounts",
        "vehicle",
        existing_type=sa.String(length=66),
        type_=mysql.VARCHAR(length=126),
        existing_nullable=True,
    )
    op.alter_column(
        "accounts", "civilite", existing_type=mysql.VARCHAR(length=10), nullable=True
    )
    op.alter_column(
        "accounting_operation",
        "debit",
        existing_type=sa.Float(precision=2),
        type_=mysql.FLOAT(),
        existing_nullable=True,
    )
    op.alter_column(
        "accounting_operation",
        "credit",
        existing_type=sa.Float(precision=2),
        type_=mysql.FLOAT(),
        existing_nullable=True,
    )
    op.alter_column(
        "accounting_operation",
        "balance",
        existing_type=sa.Float(precision=2),
        type_=mysql.FLOAT(),
        existing_nullable=True,
    )
    ### end Alembic commands ###
