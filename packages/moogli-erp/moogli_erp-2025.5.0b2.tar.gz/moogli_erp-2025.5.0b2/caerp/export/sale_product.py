from copy import deepcopy
from typing import Any

import colander

from caerp import version
from caerp.export.utils import JSONExportSQLAlchemySchemaNode
from caerp.models.company import Company
from caerp.models.sale_product import (
    BaseSaleProduct,
    SaleProductTraining,
    SaleProductWork,
)
from caerp.models.sale_product.training import SaleProductVAE

"""
These schemas are used for Sales catalog JSON import/export and validation


Some implementation choices about what is included or not in the export:

ID FIELD :

BaseSaleProduct.id are included within the export. This id will be used as a
temporary reference at import time (ex: for the relationship
WorkItem.base_sale_product->BaseSaleProduct

RELATIONSHIPS:

For models related to the exported models, FKs are not exported, instead, they
are exported as nested structures, with two different cases:

- If the relationship (eg: category) is meant to be recreated on the importer server, they are
  exported with the maximum information, including the ID of the related
  instance
- if the relationship (ex: purchase_type) is meant to be mapped to an existing object on the importer server, they are exported with just the required fields to make a lookup
"""


def walk_and_replace(cstruct, look_for: Any, replace_by: Any) -> None:
    """
    Recursive in-place search/replace in a dict/list nested structure

    Used for colander cstructs

    :param look_for: cannot be a dict/list
    """
    if isinstance(cstruct, (dict, list)):
        if isinstance(cstruct, dict):
            items = cstruct.items()
        elif isinstance(cstruct, list):
            items = enumerate(cstruct)

        for key, value in items:
            if isinstance(value, (dict, list)):
                walk_and_replace(value, look_for, replace_by)
            elif value == look_for:
                cstruct[key] = replace_by


class BaseSaleProductSchema(JSONExportSQLAlchemySchemaNode):
    CLASS = BaseSaleProduct
    OVERRIDES = {
        "supplier": {
            "default": colander.drop,
            "includes": ["label"],
        },
        "purchase_type": {
            "default": colander.drop,
            "includes": ["label"],
        },
        "product": {
            "default": colander.drop,
            "overrides": {
                "tva": {
                    "includes": ["value", "compte_cg"],
                },
            },
            "excludes": ["id", "tva_id"],
        },
        "category": {
            "default": colander.drop,
            # ID is kept to avoid creating several times the same category during import
            "includes": ["id", "description", "title"],
        },
        "tva": {
            "default": colander.drop,
            "includes": ["value", "compte_cg"],
        },
        "stock_operations": {
            "default": [],
            "excludes": [
                "id",
                # Handled on the other side on relationship:
                "base_sale_product",
                "base_sale_product_id",
            ],
        },
    }
    EXCLUDES = [
        "company",
        "company_id",
        "tva_id",
        "work_items",  # We handle it via the other side of relationship
        "category_id",
        "supplier_id",
        "tva_id",
        "product_id",
        "purchase_type_id",
    ]


class SaleProductWorkSchema(BaseSaleProductSchema):
    CLASS = SaleProductWork
    OVERRIDES = deepcopy(BaseSaleProductSchema.OVERRIDES)
    OVERRIDES.update(
        {
            "items": {
                "default": [],
                "excludes": [
                    "id",
                    "company_id",
                    "company",  # could be a long way…
                    "base_sale_product",  # We need nothing more than the id here
                    "sale_product_work",  # We handle it the other way
                    "sale_product_work_id",
                ],
            },
        }
    )


class SaleProductTrainingSchema(SaleProductWorkSchema):
    CLASS = SaleProductTraining

    OVERRIDES = deepcopy(SaleProductWorkSchema.OVERRIDES)
    OVERRIDES.update(
        {
            "types": {
                "default": [],
                "excludes": ["id"],
            },
        }
    )


class SaleProductVAESchema(SaleProductTrainingSchema):
    CLASS = SaleProductVAE


class CaerpSalesCatalogExportSchema(colander.MappingSchema):
    """

    Structure of the whole JSON of exported/imported data

    It includes metadata and the data itself.

    As of now MoOGLi supports only import/export between the same minor version..
    That means data cannot be exported from MoOGLi 6.6 and imported in 6.7. But 6.6.1->6.6.2 is ok
    Guaranteeing that has a cost that we might not want to handle for now…
    A workaround "at your own risks" is to change the version in the JSON.
    """

    VERSION = f"caerp{version(strip_suffix=True)}/sales_catalog"
    data_format = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf([VERSION]),
    )

    @colander.instantiate()
    class data(colander.MappingSchema):
        base_sale_products = colander.SequenceSchema(
            children=[BaseSaleProductSchema()],
        )
        sale_products_works = colander.SequenceSchema(
            children=[SaleProductWorkSchema()]
        )
        sale_products_trainings = colander.SequenceSchema(
            children=[SaleProductTrainingSchema()]
        )
        sale_products_vaes = colander.SequenceSchema(children=[SaleProductVAESchema()])


def serialize_catalog(company: Company) -> dict:
    """
    Serialize the catalog of sale products for a given company

    Ignore archived products.
    :param company:
    :return: the whole catalog, serialized in a JSON-compatible form.
    """
    export_schema = CaerpSalesCatalogExportSchema()
    queries = {
        "base_sale_products": BaseSaleProduct.query().filter(
            BaseSaleProduct.type_.in_(
                [
                    "sale_product_product",
                    "sale_product_material",
                    "sale_product_work_force",
                    "sale_product_service_delivery",
                ]
            )
        ),
        "sale_products_works": SaleProductWork.query().filter(
            BaseSaleProduct.type_ == "sale_product_work"
        ),
        "sale_products_trainings": SaleProductTraining.query().filter(
            BaseSaleProduct.type_ == "sale_product_training"
        ),
        "sale_products_vaes": SaleProductVAE.query().filter(
            BaseSaleProduct.type_ == "sale_product_vae"
        ),
    }

    out = {
        "data_format": export_schema.VERSION,
        "data": {},
    }

    for data_key, data_query in queries.items():
        query = data_query.filter_by(company=company)
        schema = export_schema["data"][data_key].children[0]

        products = []
        for product in query:
            appstruct = schema.dictify(product)
            products.append(appstruct)

        out["data"][data_key] = products

    serialized = export_schema.serialize(out)

    walk_and_replace(serialized, colander.null, None)
    return serialized
