import json

import colander

from caerp.export.sale_product import CaerpSalesCatalogExportSchema
from caerp.forms.files import FileNode


def validate_sales_catalog_schema(node: colander.Schema, value: dict):
    """
    Validate the JSON catalog against JSON schema
    """
    data_schema = CaerpSalesCatalogExportSchema()

    try:
        value["fp"].seek(0)
        json_decoded = json.load(value["fp"])
        data_schema.deserialize(json_decoded)
    except colander.Invalid as e:
        raise colander.Invalid(node, f"Le fichier n'est pas au bon format : {e}")
    except json.JSONDecodeError as e:
        raise colander.Invalid(
            node, f"Le fichier ne semble pas être au format JSON : {e}"
        )


class JSONSalesCatalogImportSchema(colander.Schema):
    csv_file = FileNode(
        title="Fichier JSON",
        description="Fichier JSON contenant le catalogue (exporté depuis MoOGLi)",
        validator=validate_sales_catalog_schema,
    )
