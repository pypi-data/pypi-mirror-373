"""2024.3.0 coordonees geographiques enseigne

Revision ID: 9cb9b960cd52
Revises: 303f11e5dbd4
Create Date: 2024-02-14 17:11:16.917777

"""

# revision identifiers, used by Alembic.
revision = "9cb9b960cd52"
down_revision = "303f11e5dbd4"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

import csv
import requests
from io import StringIO

import logging
import sys

logger = logging.getLogger(__name__)

address_api = "https://api-adresse.data.gouv.fr/search/csv/"


def update_database_structure():
    op.add_column("company", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("company", sa.Column("longitude", sa.Float(), nullable=True))


def migrate_datas():
    from alembic.context import get_bind
    from zope.sqlalchemy import mark_changed
    from caerp_base.models.base import DBSESSION

    session = DBSESSION()
    conn = get_bind()

    req = sa.text(
        """
        select id, address, zip_code, city
        from company
        where address is not null
        and zip_code is not null
        and address != ''
        and zip_code != ''
        """
    )

    fieldnames = ["id", "address", "zip_code", "city"]

    # create temp csv file from records
    records = conn.execute(req).fetchall()
    tempfile = StringIO()
    tempcsv = csv.writer(tempfile)
    tempcsv.writerow(fieldnames)
    for r in records:
        tempcsv.writerow([r["id"], r["address"], r["zip_code"], r["city"]])
    tempfile.seek(0)

    # send the query for mass address
    payload = {
        "columns": ["address", "city"],
        "postcode": "zip_code",
    }
    files = {"data": tempfile}

    response = requests.post(address_api, data=payload, files=files)
    logger.info("waiting for response from %s", address_api)
    response.raise_for_status()
    logger.info("server responded %s", response.status_code)

    if response.status_code != requests.codes.ok:
        logger.error("unexpected code result !")
        raise Exception(
            "Unexpected status_code {} from {} while fullfilling companies coordinates".format(
                response.status_code,
                address_api,
            )
        )
    else:
        update_companies_location(conn, response)

    mark_changed(session)
    session.flush()


def update_companies_location(conn, response):
    csvresponse = csv.DictReader(StringIO(response.text))
    csvresponse = [dict(row) for row in csvresponse]

    req = sa.text(
        """
        update company
        set
          latitude=:latitude,
          longitude=:longitude
        where id=:id_
        """
    )

    for row in csvresponse:
        if row["result_status"] != "ok":
            logger.warning(
                "Cannot get coordinates for company %s (result_status=%s)",
                row["id"],
                row["result_status"],
            )
        elif float(row["result_score"]) < 0.2:
            logger.warning(
                "Ignoring coordinates for company %s (score=%s)",
                row["id"],
                row["result_score"],
            )
        else:
            conn.execute(
                req,
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                id_=row["id"],
            )


def upgrade():
    logger = logging.getLogger("caerp")
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)
    update_database_structure()
    migrate_datas()


def downgrade():
    op.drop_column("company", "longitude")
    op.drop_column("company", "latitude")
