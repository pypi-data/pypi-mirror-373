import logging
from collections import OrderedDict
from sqlalchemy import (
    Date,
    DateTime,
    Float,
    Integer,
    Numeric,
    Boolean,
)
from sqlalchemy.orm.interfaces import ONETOMANY
from sqlalchemy.orm import (
    RelationshipProperty,
)
from sqla_inspect.base import BaseSqlaInspector
from caerp.models.user.userdatas import UserDatas


logger = logging.getLogger(__name__)


class Column(dict):
    """
    The column object wrapping the model's attribute
    """

    def __json__(self, request):
        return dict(
            label=self.get("label"),
            name=self.get("name"),
            key=self.get("key"),
            type=self.get("type", "string"),
        )


def get_data_type(datas):
    """
    Returns the type of datas

    :param obj prop: The column object returned by the sqlalchemy model
    inspection
    :returns: A string representing the type of the column
    """
    type_ = "string"
    if "options" in datas:
        return "static_opt"

    prop = datas["prop"]
    sqla_column = prop.columns[0]

    column_type = getattr(sqla_column.type, "impl", sqla_column.type)

    if isinstance(column_type, (Date, DateTime)):
        type_ = "date"
    elif isinstance(column_type, (Integer, Numeric, Float)):
        type_ = "number"
    elif isinstance(column_type, Boolean):
        type_ = "bool"
    return type_


class StatisticInspector(BaseSqlaInspector):
    """
    A sqla inspector made for statistics

    model

        The model we want to inspect

    excludes

        The name of the attributes we want to exclude from inspection

    exclude_relationships

        Should we exclude relationships (usefull for limiting recursive
        inspection)



    >>> inspector = StatisticInspector(UserDatas)
    >>> inspector.__json__()

    >>> {
    >>>     'attributes': {'key': {column statistic definition dict}},
    >>>     "relationships": {
    >>>         'key': {
    >>>             'table': {'the rel statistic definition dict (label
    ...)}
    >>>             'attributes: {....},
    >>>             'relationships': {....},
    >>>         }
    >>>     }
    >>> }


    >>> column_description = inspector.get(key)
    """

    config_key = "stats"

    def __init__(self, model, excludes=(), exclude_relationships=False):
        BaseSqlaInspector.__init__(self, model)
        self.model = model
        self.excludes = excludes
        self.exclude_relationships = exclude_relationships
        self.columns = self._collect_columns()

    def _get_label(self, colanderalchemy_infos, stats_infos, key):
        if "label" in stats_infos:
            return stats_infos["label"]
        else:
            return colanderalchemy_infos.get("title", key)

    def _collect_columns(self):
        """
        Collect the columns names, titles, ...

        Single attribute :
            name: for column identification
            label : for UI
            prop : The property (sqla object from which handle all datas
            column : The associated sqlalchemy.Column object

        OneToMany relationship :
            related_class: The related class
            related_key: The related key we may act on

        ManyToOne relationship :
            for each field of the destination class:
                related_class: The related_class
                name: for column identification
                label : for UI
                prop : The property (sqla object from which handle all datas
                column : The associated sqlalchemy.Column object


        """
        result = OrderedDict()
        todrop = []
        for prop in self.get_sorted_columns():
            if prop.key in self.excludes:
                continue
            info_dict = self.get_info_field(prop)
            colanderalchemy_infos = info_dict.get("colanderalchemy", {})

            export_infos = info_dict.get("export", {}).copy()
            stats_infos = export_infos.get(self.config_key, {}).copy()

            if "exclude" in stats_infos:
                if stats_infos["exclude"]:
                    continue
            elif export_infos.get("exclude", False):
                continue

            infos = export_infos
            infos.update(stats_infos)

            ui_label = self._get_label(colanderalchemy_infos, stats_infos, prop.key)
            section = colanderalchemy_infos.get("section", "")
            if section:
                ui_label = "{0} : {1}".format(section, ui_label)
            datas = Column(
                {
                    "name": prop.key,
                    "label": ui_label,
                    "prop": prop,
                    "column": prop.class_attribute,
                    "section": section,
                    "key": prop.key,
                }
            )
            datas.update(infos)

            if isinstance(prop, RelationshipProperty):
                if prop.direction == ONETOMANY:
                    if prop.uselist:
                        # Relation o2M
                        # A one to many relationship
                        if self.exclude_relationships:
                            # On zappe les relations o2M
                            continue

                        # On construit un inspecteur pour le table liée
                        datas["inspector"] = StatisticInspector(
                            prop.mapper,
                            self.excludes,
                        )
                        datas["type"] = "onetomany"
                        # On référence la table liée
                        datas["table"] = prop.mapper.class_
                        # On récupère le nom de la FK qui pointe sur notre modèle
                        datas["remote_side_id"] = list(prop.remote_side)[0].key
                        result[prop.key] = datas
                    else:
                        # Relation OneToOne
                        datas["inspector"] = StatisticInspector(
                            prop.mapper,
                            self.excludes,
                        )
                        datas["type"] = "onetoone"
                        # On référence la table liée
                        datas["table"] = prop.mapper.class_
                        # On récupère le nom de la FK qui pointe sur notre modèle
                        datas["remote_side_id"] = list(prop.remote_side)[0].key
                        result[prop.key] = datas
                else:
                    # On doit avoir directement les ids des options (objets
                    # distants) disponibles
                    # (sera fait lors de la génération du schéma)

                    # On utilisera la colonne avec l'id
                    fkey = "%s_id" % prop.key
                    todrop.append(fkey)
                    datas["type"] = "manytoone"
                    datas["foreign_key"] = fkey
                    # On a besoin de la classe liée pour la génération du form
                    # (récupérer les options disponibles)
                    datas["related_class"] = prop.mapper.class_
                    result[datas["name"]] = datas
            else:
                datas["type"] = get_data_type(datas)
                result[datas["name"]] = datas

        for id_key in todrop:
            if id_key in result:
                ui_label = result[id_key].get("label")
                rel_key = id_key[:-3]
                if rel_key in result:
                    result[rel_key]["label"] = ui_label
                    result[rel_key]["column"] = result[id_key]["column"]
                result.pop(id_key)
        return result

    def get(self, key):
        """
        Return the inspected datas for the key

        :param str key: A column name
        """
        return self.columns.get(key)
        # if key in self.columns['attributes']:
        #     return self.columns['attributes'].get(key)
        # else:
        #     return self.columns['relationships'].get(key)

    def __json__(self, request):
        """
        Return the json representation of this inspector
        """
        result = {
            "attributes": OrderedDict(),
        }
        for key, value in self.columns.items():
            if "inspector" in value:
                result.setdefault("relationships", OrderedDict())
                # C'est une autre table (o2m relationship)
                # On collecte les infos sur la relation
                data = value.__json__(request)
                # On complète les données sur les colonnes :
                #     lancement récursif cette méthode (__json__)
                data.update(value["inspector"].__json__(request))
                result["relationships"][key] = data

            else:
                result["attributes"][key] = value.__json__(None)
        return result


def get_inspector(model=UserDatas):
    """
    Return a statistic inspector for the given model
    """
    return StatisticInspector(
        model,
        excludes=(
            "parent_id",
            "children",
            "type_",
            "_acl",
            "id",
            "parent",
        ),
    )
