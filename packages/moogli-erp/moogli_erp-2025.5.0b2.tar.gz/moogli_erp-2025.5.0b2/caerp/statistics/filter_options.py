"""
Filter options used in the query_helper and presented to the end user in the UI
"""
STRING_OPTIONS = (
    {"value": "has", "label": "Contenant"},
    {"value": "sw", "label": "Commençant par"},
    {"value": "ew", "label": "Se terminant par"},
    {"value": "nhas", "label": "Ne contenant pas"},
    {"value": "neq", "label": "N'étant pas égal(e) à"},
    {"value": "eq", "label": "Étant égal(e) à"},
    {"value": "nll", "label": "N'étant pas renseigné(e)"},
    {"value": "nnll", "label": "Étant renseigné(e)"},
)


BOOL_OPTIONS = (
    {"value": "true", "label": "Étant coché(e)"},
    {"value": "false", "label": "N'étant pas coché(e)"},
)


OPTREL_OPTIONS = (
    {"value": "ioo", "label": "Faisant partie de"},
    {"value": "nioo", "label": "Ne faisant pas partie de"},
    {"value": "nll", "label": "N'étant pas renseigné(e)"},
    {"value": "nnll", "label": "Étant renseigné(e)"},
)


NUMERIC_OPTIONS = (
    {"value": "lte", "label": "Étant inférieur(e) ou égal(e)"},
    {"value": "gte", "label": "Étant supérieur(e) ou égal(e)"},
    {"value": "bw", "label": "Faisant partie de l'intervalle"},
    {"value": "nbw", "label": "Ne faisant pas partie de l'intervalle"},
    {"value": "eq", "label": "Étant égal(e) à"},
    {"value": "neq", "label": "N'étant pas égal(e) à"},
    {"value": "lt", "label": "Étant inférieur(e) à"},
    {"value": "gt", "label": "Étant supérieur(e) à"},
    {"value": "nll", "label": "N'étant pas renseigné(e)"},
    {"value": "nnll", "label": "Étant renseigné(e)"},
)


DATE_OPTIONS = (
    {"value": "dr", "label": "Dans l'intervalle"},
    {"value": "ndr", "label": "Pas dans l'intervalle"},
    {"value": "this_year", "label": "Depuis le début de l'année"},
    {"value": "this_month", "label": "Ce mois-ci"},
    {"value": "previous_year", "label": "L'année dernière"},
    {"value": "previous_month", "label": "Le mois dernier"},
    {"value": "nll", "label": "N'étant pas renseigné(e)"},
    {"value": "nnll", "label": "Étant renseigné(e)"},
)


MULTIDATE_OPTIONS = (
    {"value": "first_dr", "label": "Le premier dans l'intervalle"},
    {"value": "first_this_year", "label": "Le premier depuis le début de l'année"},
    {"value": "first_this_month", "label": "Le premier ce mois-ci"},
    {"value": "first_previous_year", "label": "Le premier l'année dernière"},
    {"value": "first_previous_month", "label": "Le premier le mois dernier"},
    {"value": "last_dr", "label": "Le dernier dans l'intervalle"},
    {"value": "last_this_year", "label": "Le dernier depuis le début de l'année"},
    {"value": "last_this_month", "label": "Le dernier ce mois-ci"},
    {"value": "last_previous_year", "label": "Le dernier l'année dernière"},
    {"value": "last_previous_month", "label": "Le dernier le mois dernier"},
    {"value": "nll", "label": "N'étant pas renseigné(e)"},
    {"value": "nnll", "label": "Étant renseigné(e)"},
)

STATISTIC_FILTER_OPTIONS = {
    "date": DATE_OPTIONS,
    "number": NUMERIC_OPTIONS,
    "string": STRING_OPTIONS,
    "manytoone": OPTREL_OPTIONS,
    "static_opt": OPTREL_OPTIONS,
    "bool": BOOL_OPTIONS,
    "multidate": MULTIDATE_OPTIONS,
}
