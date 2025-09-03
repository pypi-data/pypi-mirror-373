"""4.3 Migrate customers to third parties

Revision ID: 434b21bf4934
Revises: 432e6cd0752c
Create Date: 2019-02-18 17:05:49.481432

"""

# revision identifiers, used by Alembic.
revision = "434b21bf4934"
down_revision = "2abf64552d74"

from alembic import op
import sqlalchemy as sa
from caerp_base.models.base import DBSESSION
from zope.sqlalchemy import mark_changed
from caerp.alembic.utils import (
    disable_constraints,
    enable_constraints,
)


def upgrade():
    session = DBSESSION()
    conn = op.get_bind()
    disable_constraints()

    # CREATION DES HELPERS
    customer_helper = sa.Table(
        "customer",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("company_id", sa.Integer),
        sa.Column("type_", sa.String(10)),
        sa.Column("code", sa.String(4)),
        sa.Column("label", sa.String(255)),
        sa.Column("name", sa.String(255)),
        sa.Column("civilite", sa.String(10)),
        sa.Column("lastname", sa.String(255)),
        sa.Column("firstname", sa.String(255)),
        sa.Column("function", sa.String(255)),
        sa.Column("registration", sa.String(50)),
        sa.Column("address", sa.String(255)),
        sa.Column("zip_code", sa.String(20)),
        sa.Column("city", sa.String(255)),
        sa.Column("country", sa.String(150)),
        sa.Column("email", sa.String(255)),
        sa.Column("mobile", sa.String(20)),
        sa.Column("phone", sa.String(50)),
        sa.Column("fax", sa.String(50)),
        sa.Column("tva_intracomm", sa.String(50)),
        sa.Column("comments", sa.Text),
        sa.Column("compte_cg", sa.String(125)),
        sa.Column("compte_tiers", sa.String(125)),
        sa.Column("archived", sa.Boolean),
        sa.Column("created_at", sa.Date),
        sa.Column("updated_at", sa.Date),
    )
    third_party_helper = sa.Table(
        "third_party",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("company_id", sa.Integer),
        sa.Column("type", sa.String(10)),
        sa.Column("code", sa.String(4)),
        sa.Column("label", sa.String(255)),
        sa.Column("company_name", sa.String(255)),
        sa.Column("civilite", sa.String(10)),
        sa.Column("lastname", sa.String(255)),
        sa.Column("firstname", sa.String(255)),
        sa.Column("function", sa.String(255)),
        sa.Column("registration", sa.String(50)),
        sa.Column("address", sa.String(255)),
        sa.Column("zip_code", sa.String(20)),
        sa.Column("city", sa.String(255)),
        sa.Column("country", sa.String(150)),
        sa.Column("email", sa.String(255)),
        sa.Column("mobile", sa.String(20)),
        sa.Column("phone", sa.String(50)),
        sa.Column("fax", sa.String(50)),
        sa.Column("tva_intracomm", sa.String(50)),
        sa.Column("comments", sa.Text),
        sa.Column("compte_cg", sa.String(125)),
        sa.Column("compte_tiers", sa.String(125)),
        sa.Column("archived", sa.Boolean),
    )
    node_helper = sa.Table(
        "node",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255)),
        sa.Column("created_at", sa.Date),
        sa.Column("updated_at", sa.Date),
        sa.Column("parent_id", sa.Integer),
        sa.Column("type_", sa.String(30)),
        sa.Column("_acl", sa.Text),
    )

    # MIGRATION DES CLIENTS EN TIERS
    customers_ids = []
    for customer in conn.execute(customer_helper.select()):
        req = conn.execute(
            node_helper.insert().values(
                name=customer.label,
                created_at=customer.created_at,
                updated_at=customer.updated_at,
                type_="customer",
            )
        )
        node_id = req.inserted_primary_key[0]
        customers_ids.append((customer.id, node_id))
        conn.execute(
            third_party_helper.insert().values(
                id=node_id,
                company_id=customer.company_id,
                type=customer.type_,
                code=customer.code,
                label=customer.label,
                company_name=customer.name,
                civilite=customer.civilite,
                lastname=customer.lastname,
                firstname=customer.firstname,
                function=customer.function,
                registration=customer.registration,
                address=customer.address,
                zip_code=customer.zip_code,
                city=customer.city,
                country=customer.country,
                email=customer.email,
                mobile=customer.mobile,
                phone=customer.phone,
                fax=customer.fax,
                tva_intracomm=customer.tva_intracomm,
                comments=customer.comments,
                compte_cg=customer.compte_cg,
                compte_tiers=customer.compte_tiers,
                archived=customer.archived,
            )
        )

    # MODIFICATION DE LA TABLE 'customer'
    try:
        op.drop_constraint("customer_ibfk_1", "customer", type_="foreignkey")
    except:
        pass
    try:
        op.drop_constraint("fk_customer_company_id", "customer", type_="foreignkey")
    except:
        pass
    op.create_foreign_key(
        op.f("fk_customer_id"), "customer", "third_party", ["id"], ["id"]
    )
    op.drop_column("customer", "code")
    op.drop_column("customer", "updated_at")
    op.drop_column("customer", "registration")
    op.drop_column("customer", "city")
    op.drop_column("customer", "archived")
    op.drop_column("customer", "compte_cg")
    op.drop_column("customer", "compte_tiers")
    op.drop_column("customer", "company_id")
    op.drop_column("customer", "comments")
    op.drop_column("customer", "label")
    op.drop_column("customer", "email")
    op.drop_column("customer", "zip_code")
    op.drop_column("customer", "function")
    op.drop_column("customer", "fax")
    op.drop_column("customer", "firstname")
    op.drop_column("customer", "lastname")
    op.drop_column("customer", "phone")
    op.drop_column("customer", "address")
    op.drop_column("customer", "name")
    op.drop_column("customer", "mobile")
    op.drop_column("customer", "country")
    op.drop_column("customer", "created_at")
    op.drop_column("customer", "type_")
    op.drop_column("customer", "tva_intracomm")
    op.drop_column("customer", "civilite")
    op.execute("DELETE FROM `customer` WHERE 1")

    # INSERTION DES NOUVEAUX IDS DES CLIENTS
    new_customer_helper = sa.Table(
        "customer", sa.MetaData(), sa.Column("id", sa.Integer, primary_key=True)
    )
    for old_id, new_id in customers_ids:
        conn.execute(new_customer_helper.insert().values(id=new_id))

    # MISE A JOUR DES CLES ETRANGERES
    customers_ids.sort(key=lambda id: id[0], reverse=True)
    for old_id, new_id in customers_ids:
        op.execute(
            "UPDATE task SET customer_id={} WHERE customer_id={}".format(new_id, old_id)
        )
        op.execute(
            "UPDATE project_customer SET customer_id={} WHERE customer_id={}".format(
                new_id, old_id
            )
        )

    mark_changed(session)
    session.flush()
    enable_constraints()


def downgrade():
    pass
