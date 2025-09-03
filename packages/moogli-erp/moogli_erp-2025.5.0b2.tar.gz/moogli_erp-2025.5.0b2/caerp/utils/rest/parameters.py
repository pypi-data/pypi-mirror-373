"""
Parameters management for the V2 API formats

Query parameters :

- Filters
- Pagination
- Sorting
- Fields

Json response data structure :

- Data : The data to be returned
- Meta : The meta information about the response
"""


import typing
from dataclasses import dataclass

import colander

from caerp.consts import PAGINATION_DEFAULT_PAGE, PAGINATION_DEFAULT_PER_PAGE


def split_expand_fields(expand_parameter_string: str) -> list:
    """
    Splits a string of fields into a list, preserving nested fields within brackets.
    Used to manage the Fields query parameters.

    >>> split_expand_fields('name,books[title,publication_date,library[name,address],number_of_pages],firstname,dateofbirth')
    ['name', 'books[title,publication_date,library[name,address],number_of_pages]', 'firstname', 'dateofbirth']
    """
    result = []
    current_field = []
    bracket_depth = 0

    for char in expand_parameter_string:
        if char == "," and bracket_depth == 0:
            if current_field:
                result.append("".join(current_field))
                current_field = []
        else:
            current_field.append(char)
            if char == "[":
                bracket_depth += 1
            elif char == "]":
                bracket_depth -= 1

    if current_field:
        result.append("".join(current_field))

    return result


def parse_expand_field_parameters(expand_parameter_string: str) -> dict:
    """
    Parse data query string into nested dictionary representing the
    expected relationship output.

    Here we query the /api/v2/authors

    >>> parse_expand_field_parameters('firstname,lastname,books[title,publication_date]')
    {
        "attributes": ["firstname", "lastname"],
        "relationships": {
            "books": {
                "attributes": ["title", "publication_date"],
                "relationships": {}
            }
        }
    }
    """
    if not expand_parameter_string:
        return {"attributes": [], "relationships": {}}

    result = {"attributes": [], "relationships": {}}
    current = result

    def process_item(item, current):
        if "[" in item:
            relation, attrs = item.split("[", 1)
            relation = relation.strip()
            attrs = attrs.rstrip("]")
            current["relationships"][relation] = parse_expand_field_parameters(attrs)
            return current
        else:
            current["attributes"].append(item.strip())
            return current

    items = split_expand_fields(expand_parameter_string)
    for item in items:
        current = process_item(item, current)

    return result


@dataclass
class FieldOptions:
    attributes: typing.Optional[typing.List[str]]
    relationships: typing.Optional[typing.Dict[str, "FieldOptions"]]

    def __init__(
        self,
        attributes: typing.Optional[typing.List[str]] = None,
        relationships_dict: typing.Optional[typing.Dict] = None,
    ):
        self.attributes = attributes or []
        self.relationships = {}

        if relationships_dict is not None:
            for key, rel_def in relationships_dict.items():

                # Cas où on utilise des FieldOptions existant déjà
                if isinstance(rel_def, self.__class__):
                    self.relationships[key] = rel_def
                else:
                    attributes = rel_def.get("attributes")
                    relationships_dict = rel_def.get("relationships")
                    self.relationships[key] = FieldOptions(
                        attributes=attributes,
                        relationships_dict=relationships_dict,
                    )

    @classmethod
    def from_request(cls, request):
        fields = parse_expand_field_parameters(request.params.get("fields"))
        return cls.from_dict(fields)

    @classmethod
    def from_dict(cls, fields: dict):
        return cls(
            attributes=fields.get("attributes"),
            relationships_dict=fields.get("relationships"),
        )


class PaginationSchema(colander.MappingSchema):
    page = colander.SchemaNode(
        colander.Integer(),
        default=PAGINATION_DEFAULT_PAGE,
        missing=PAGINATION_DEFAULT_PAGE,
        validator=colander.Range(min=PAGINATION_DEFAULT_PAGE),
        title="Numéro de page",
    )
    per_page = colander.SchemaNode(
        colander.Integer(),
        default=PAGINATION_DEFAULT_PER_PAGE,
        missing=PAGINATION_DEFAULT_PER_PAGE,
        validator=colander.Range(min=-1, max=1000000),
    )


@dataclass
class PaginationOptions:
    """
    Dataclass representing pagination options.

    Page numbers start at 1
    """

    page: int = PAGINATION_DEFAULT_PAGE
    per_page: int = PAGINATION_DEFAULT_PER_PAGE

    @classmethod
    def from_request(cls, request):
        """
        :raises: colander.Invalid - if the request pagination parameters are not valid.
        """
        request_params = dict(
            page=request.params.get("pagination.page"),
            per_page=request.params.get("pagination.per_page"),
        )

        pagination_data = PaginationSchema().deserialize(request_params)
        return cls(**pagination_data)


class SortSchema(colander.MappingSchema):
    sort = colander.SchemaNode(colander.String(), title="Colonne de tri", missing=None)
    sort_direction = colander.SchemaNode(
        colander.String(),
        title="Ordre de tri",
        default="asc",
        missing="asc",
        validator=colander.OneOf(["asc", "desc"]),
    )


@dataclass
class SortOptions:
    """
    Dataclass representing sort options.
    """

    sort: typing.Optional[str] = None
    sort_direction: typing.Optional[str] = "asc"

    @classmethod
    def from_request(cls, request):
        """
        :raises: colander.Invalid - if the request sort parameters are not valid.
        """
        request_params = dict(
            sort=request.params.get("sort.sort"),
            sort_direction=request.params.get("sort.sortDirection"),
        )

        sort_data = SortSchema().deserialize(request_params)
        return cls(**sort_data)


@dataclass
class LoadOptions:
    """
    Dataclass representing load options.
    Converts the query parameters into a LoadOptions object.


    Example of a query string :

        ?search=<searchedValue>&filter_field=<value>&filter_field2=<value>&sort.sort=<fieldname>&sort.sortDirection=<asc|desc>&pagination.page=<pagenumber>&pagination.per_page=<pagesize>
    """

    search: typing.Optional[str] = None
    filters: typing.Optional[dict] = None
    fields: typing.Optional[FieldOptions] = None
    pagination: typing.Optional[PaginationOptions] = None
    sort: typing.Optional[SortOptions] = None

    @classmethod
    def from_request(cls, request):
        return cls(
            # les filters sont passés en paramètre sous filter_<nom>
            # On retire le prefix filter_
            filters=dict(
                [
                    (key[7:], value)
                    for key, value in request.params.items()
                    if key.startswith("filter_")
                ]
            ),
            fields=FieldOptions.from_request(request),
            pagination=PaginationOptions.from_request(request),
            sort=SortOptions.from_request(request),
        )


@dataclass
class RestCollectionMetadata:
    total_count: int
    pagination: typing.Optional[PaginationOptions] = None
    total_pages: typing.Optional[int] = 1

    def __json__(self, request):
        result: typing.Dict[str, typing.Any] = {
            "total_count": self.total_count,
        }
        if self.pagination is None:
            result["per_page"] = None
            result["page"] = 1
            result["total_pages"] = 1
        else:
            result["page"] = self.pagination.page
            result["per_page"] = self.pagination.per_page
            # // est une operation entière  5 // 2  = 2
            result["total_pages"] = self.total_count // self.pagination.per_page + (
                1 if self.total_count % self.pagination.per_page else 0
            )
        return result


@dataclass
class RestCollectionResponse:
    """
    A dataclass representing a response from a collection endpoint.
    """

    items: typing.List[typing.Dict]
    metadata: RestCollectionMetadata

    def __json__(self, request):
        return {
            "items": self.items,
            "metadata": self.metadata,
        }
