import logging
from typing import List, Tuple, Any, Union

from caerp.utils.rest.parameters import FieldOptions

logger = logging.getLogger(__name__)


def force_list(value: Any) -> Union[List, Tuple]:
    if not isinstance(value, (list, tuple)):
        if value is None:
            value = []
        else:
            value = [value]

    return value


class BaseSerializer:
    """
    Base implementation of a serializer

    A serializer :

    - Convert a model to a dictionary
    - Check the permissions on attributes or relationships of the current user

    It takes

    fields

        a dictionary describing the fields and relationships to serialize (see utils/rest.py for the format)

    serializer_registry

        a dictionary mapping model names to their serializers

    excludes

        a list of fields to exclude from serialization (to avoid circular serialization issues)

    A subclass should implement:

    acl

        A dictionary mapping field (or relationship) names to their permissions (global or item based permissions are both supported)
        Example

        .. code-block:: python

            acl = {
                'id': 'global.authenticated',
                'name': ['global.company_view', 'context.edit'],
                'compte_cg': "context.edit"
            }

        A special __all__ key can be used as a default for all attributes (not relationships)

        Example

        .. code-block:: python

            acl = {
                '__all__': 'global.authenticated',
                'compte_tiers': 'global.company_view',
                'compte_cg': "context.edit"
            }


    For each value, the process is as follows:

        - We check the permission
        - We get the value
        - We format the value (only for model attributes, not for relationships,
        relationships' data are formatted in its dedicated serializer)

    Some methods can be implemented to interfere into the serialization process.
    The subclass can implement:

        get_{field_name}(request, item, field_name)

            A specific method to customize the production of a specific field value
            Example

            .. code-block:: python

                def get_chiffre_affaire(self, request, item, field_name):
                    return request.execute(
                        select(func.sum(Task.ttc)
                        ).where(
                            Task.company_id == item.id
                        ).where(
                            Task.type_.in_(Task.invoice_types)
                        ).where(
                            Task.status=='valid'
                        ).scalar()
                    ) or 0

        format_{field_name}(request, item, field_name)

            A specific method to customize the serialization of a specific field (only for
            model attributes, not for relationships)

            Example

            .. code-block:: python

                def format_chiffre_affaire(self, request, item, value):
                    return format_amount(value, precision=5)

    """

    acl = None
    # Used to avoid circular serialization issues
    exclude_from_children = None

    def __init__(
        self, fields: FieldOptions, serializer_registry: dict, excludes: Tuple = ()
    ):
        self.fields = fields
        self.attributes = fields.attributes or []
        self.relationships = fields.relationships or {}
        self.serializer_registry = serializer_registry
        self.excludes = excludes
        self.load_relationships_serializer(serializer_registry)
        if self.acl is None:
            raise Exception(f"No ACL defined for serializer {self.__class__.__name__}")
        elif self.exclude_from_children is None:
            raise Exception(
                f"No exclude_from_children defined for serializer {self.__class__.__name__}"
            )

    def non_plural_relationship_name(self, relation_name: str) -> str:
        """
        Convert a manytoone relationship name to a singular one
        """
        if relation_name.endswith("s"):
            return relation_name[:-1]
        return relation_name

    def load_relationships_serializer(self, serializer_registry: dict) -> dict:
        """
        Load serializers for relationships
        """
        self.relationships_serializer = {}
        for relation_name, relation_fields in self.relationships.items():
            relationship_name = self.non_plural_relationship_name(relation_name)
            serializer = serializer_registry.get(relationship_name)

            if serializer is not None:
                self.relationships_serializer[relation_name] = serializer(
                    relation_fields,
                    serializer_registry,
                    # On évite les récursions
                    excludes=self.exclude_from_children,
                )

        return self.relationships_serializer

    def is_attribute_allowed(self, request, item, attribute: str) -> bool:
        """
        Check if a field is allowed in export for the current user
        """
        global_acl = self.acl.get("__all__")
        global_acl = force_list(global_acl)
        if global_acl:
            for ace in global_acl:
                if request.has_permission(ace, item):
                    return True
        else:
            acl = self.acl.get(attribute)
            acl = force_list(acl)
            if acl:
                for ace in acl:
                    if request.has_permission(ace, item):
                        return True
        logger.warning(
            f"{self} Trying to access unauthorized field '{attribute}' for item {item}"
        )
        return False

    def is_relationship_allowed(self, request, item, relationship_name: str) -> bool:
        """
        Check if a relationship is allowed in export for the current user
        """
        if relationship_name in self.excludes:
            return False

        acl = self.acl.get(relationship_name)
        acl = force_list(acl)

        if acl:
            for ace in acl:
                if request.has_permission(ace, item):
                    return True
        logger.warning(
            f"{self} Trying to access unauthorized relationship '{relationship_name}' "
            f"for item {item} acl : {acl}"
        )
        return False

    def _get_item_value(self, request, item, field: str):
        """
        Get the value of an attribute or relationship from an item
        """
        if hasattr(self, f"get_{field}"):
            return getattr(self, f"get_{field}")(request, item, field)
        return getattr(item, field, None)

    def _format_value(self, request, item, field, db_value):
        """
        Handle value formatting looking for a format_{field} method if available
        """
        formatter = getattr(self, f"format_{field}", None)
        if formatter is not None:
            value = formatter(request, item, db_value)
        else:
            value = db_value
        return value

    def run(self, request, item) -> dict:
        """
        Serialize an item into a dictionary using the current fields and relationships
        """
        result = {}
        for field in self.attributes:
            if field in self.excludes or not self.is_attribute_allowed(
                request, item, field
            ):
                continue
            db_value = self._get_item_value(request, item, field)
            value = self._format_value(request, item, field, db_value)

            result[field] = value

        for relation_name in self.relationships:
            if relation_name in self.excludes or not self.is_relationship_allowed(
                request, item, relation_name
            ):
                continue
            serializer = self.relationships_serializer.get(relation_name)
            db_value = self._get_item_value(request, item, relation_name)
            if db_value is not None:
                if serializer is not None:
                    if isinstance(db_value, (list, set, tuple)):
                        result[relation_name] = [
                            serializer.run(request, item) for item in db_value
                        ]
                    else:
                        result[relation_name] = serializer.run(request, db_value)
                else:
                    result[relation_name] = db_value
        return result
