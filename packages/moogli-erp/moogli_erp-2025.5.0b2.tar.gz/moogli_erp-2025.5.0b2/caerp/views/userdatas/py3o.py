import logging
import os
import datetime

from caerp.consts.permissions import PERMISSIONS
from pyramid.httpexceptions import HTTPFound
from genshi.template.eval import UndefinedError
from sqla_inspect import py3o
from sqlalchemy.orm import (
    Load,
    joinedload,
)

from caerp.export.utils import write_file_to_request
from caerp.models import files
from caerp.models.user import User
from caerp.utils.widgets import (
    POSTButton,
)
from caerp.views import (
    BaseView,
    DeleteView,
)
from caerp.views.userdatas.routes import (
    USER_USERDATAS_PY3O_URL,
    TEMPLATING_ITEM_URL,
)
from caerp.views.admin.userdatas.templates import TEMPLATE_URL


logger = logging.getLogger(__name__)


def record_compilation(context, request, template):
    """
    Record the compilation of a template to be able to build an history
    """
    history = files.TemplatingHistory(
        user_id=request.identity.id, userdatas_id=context.id, template_id=template.id
    )
    logger.debug("Storing an history object")
    request.dbsession.add(history)


def get_filename(template_name, userdata_firstname, userdata_lastname):
    """
    Return the filename to use to store
    """
    now = datetime.datetime.now()
    name = os.path.splitext(template_name)[0]
    return "{0}_{1}_{2}_{3}.odt".format(
        name, userdata_firstname, userdata_lastname, now.strftime("%d-%m-%Y-%Hh-%M")
    )


def store_compiled_file(context, request, output, template):
    """
    Stores the compiled datas in the user's environment

    :param context: The context of the
    """
    logger.debug("Storing the compiled file {}".format(template.name))
    userdata_firstname = context.coordonnees_firstname
    userdata_lastname = context.coordonnees_lastname
    name = get_filename(template.name, userdata_firstname, userdata_lastname)
    output.seek(0)
    datas = output.getvalue()
    file_obj = files.File(
        name=name,
        description=template.description,
        mimetype="application/vnd.oasis.opendocument.text",
        size=len(datas),
        parent_id=context.id,
    )
    file_obj.data = output
    request.dbsession.add(file_obj)
    return file_obj


def get_error_msg_from_genshi_error(err):
    """
    Genshi raises an UndefinedError, but doesn't store the key name in the
    Exception object.
    We try to get the missing key from the resulting message and return
    a comprehensive error message for the user.
    """
    if " not defined" in err.msg:
        # Donnée non renseignée
        return "La clé '{}' n'est pas définie.".format(err.msg.split(" not defined")[0])
    elif "has no member" in err.msg:
        # Liste vide
        return """Un élément utilisé dans le modèle n'est pas présent 
        pour cet utilisateur (généralement une étape de parcours, le détail 
        d'une activité, ou un statut social)."""
    else:
        # Autre erreur
        return "Détail de l'erreur : '{}'".format(err.msg)


def get_userdatas_py3o_stage_datas(userdatas):
    """
    Generate additionnal datas that can be used for the py3o compiling context

    :param obj userdatas: The UserDatas instance
    """
    compatibility_keys = {
        "Contrat CAPE": "parcours_convention_cape",
        "Avenant contrat": "parcours_contract_history",
        "Contrat DPAE": "parcours_dpae",
    }
    res = {}
    context = None
    for stage, paths in list(userdatas.get_career_path_by_stages().items()):
        num_path = len(paths)
        for index, path in enumerate(paths):
            if context is None:
                context = py3o.SqlaContext(path.__class__)
            path_as_dict = context.compile_obj(path)

            key = stage.replace(" ", "")
            datas = res.setdefault(key, {})

            datas["l%s" % index] = path_as_dict

            if index == 0:
                datas["last"] = path_as_dict
            if index == num_path - 1:
                datas["first"] = path_as_dict

            # On veut garder les clés que l'on avait dans le passé
            if stage in compatibility_keys:
                res[compatibility_keys[stage]] = datas.copy()

    return res


def get_userdatas_company_datas(userdatas):
    """
    Generate additionnal_context datas that can be used for the py3o compiling
    context

    :param obj userdatas: The UserDatas instance
    :returns: a dict with company_datas
    """
    result = {"companydatas": {}}
    if userdatas.user:
        datas = result["companydatas"]
        context = None
        num_companies = len(userdatas.user.companies)
        for index, company in enumerate(userdatas.user.companies):
            if context is None:
                context = py3o.SqlaContext(company.__class__)
            company_dict = context.compile_obj(company)
            company_dict["title"] = company_dict["name"]
            datas["l%s" % index] = company_dict
            if index == 0:
                datas["first"] = company_dict

            if index == num_companies:
                datas["last"] = company_dict

    return result


def get_template_output(request, template, context):
    """
    Compile the template/datas and generate the output file

    Workflow :

        - The context (model) is serialized to a dict
        - py3o is used to compile the template using the given dict

    :param obj request: The current request object
    :param obj template: A Template object
    :param obj context: The context to use for templating (must be an instance
    inheriting from Node)
    :returns: The request object
    :returns: io.BytesIO
    """
    additionnal_context = get_userdatas_py3o_stage_datas(context)
    additionnal_context.update(get_userdatas_company_datas(context))
    additionnal_context.update(request.config)
    return py3o.compile_template(
        context,
        template.data_obj,
        additionnal_context=additionnal_context,
    )


class UserDatasFileGeneration(BaseView):
    """
    Base view for file generation
    """

    title = "Génération de documents sociaux"

    @property
    def current_userdatas(self):
        return self.context

    @property
    def admin_url(self):
        return self.request.route_path(TEMPLATE_URL)

    def stream_actions(self, item):
        """
        Stream actions on TemplatingHistory instances

        :param obj item: A TemplatingHistory instance
        :returns: A generator producing Link instances
        """
        yield POSTButton(
            self.request.route_path(
                TEMPLATING_ITEM_URL, id=item.id, _query={"action": "delete"}
            ),
            "Supprimer",
            icon="trash-alt",
            css="icon",
        )

    def py3o_action_view(self, doctemplate_id):
        """
        Answer to simple GET requests
        """
        model = self.current_userdatas
        template = files.Template.get(doctemplate_id)
        if template:
            logger.debug(" + Templating (%s, %s)" % (template.name, template.id))
            try:
                compiled_output = get_template_output(self.request, template, model)
                write_file_to_request(self.request, template.name, compiled_output)
                store_compiled_file(
                    model,
                    self.request,
                    compiled_output,
                    template,
                )
                record_compilation(model, self.request, template)
                return self.request.response
            except UndefinedError as err:
                msg = get_error_msg_from_genshi_error(err)
                logger.exception(msg)
                self.session.flash(
                    "<b>Erreur à la compilation du modèle</b><p>{}</p>".format(msg),
                    "error",
                )
            except IOError:
                logger.exception("Le template n'existe pas sur le disque")
                self.session.flash(
                    """<b>Erreur à la compilation du modèle</b><p>Le fichier 
                    correspondant au modèle de ce document est manquant. Merci de 
                    le recharger depuis la configuration.</p>""",
                    "error",
                )
            except Exception:
                logger.exception(
                    """Une erreur est survenue à la compilation du template {} avec 
                    un contexte de type {} et d'id {}""".format(
                        template.id,
                        model.__class__,
                        model.id,
                    )
                )
                self.session.flash(
                    """<b>Erreur à la compilation du modèle</b><p>Merci de contacter 
                    votre administrateur.</p>""",
                    "error",
                )
        else:
            logger.exception("Le template {} n'existe pas".format(doctemplate_id))
            self.session.flash(
                """<b>Erreur à la compilation du modèle</b><p>Ce modèle de document 
                n'existe pas.</p>""",
                "error",
            )

        return HTTPFound(self.request.current_route_path(_query={}))

    def __call__(self):
        doctemplate_id = self.request.GET.get("template_id")
        if doctemplate_id:
            return self.py3o_action_view(doctemplate_id)
        else:
            available_templates = files.Template.query()
            available_templates = available_templates.filter_by(active=True)
            template_query = files.TemplatingHistory.query()
            template_query = template_query.options(
                Load(files.TemplatingHistory).load_only("id", "created_at"),
                joinedload("user").load_only("firstname", "lastname"),
                joinedload("template").load_only("name"),
            )
            template_query = template_query.filter_by(
                userdatas_id=self.current_userdatas.id
            )
            return dict(
                templates=available_templates.all(),
                template_history=template_query.all(),
                title=self.title,
                current_userdatas=self.current_userdatas,
                admin_url=self.admin_url,
                stream_actions=self.stream_actions,
            )


class UserUserDatasFileGeneration(UserDatasFileGeneration):
    @property
    def current_userdatas(self):
        return self.context.userdatas


class TemplatingHistoryDeleteView(DeleteView):
    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                USER_USERDATAS_PY3O_URL, id=self.context.userdatas.user_id
            )
        )


def includeme(config):
    config.add_view(
        UserUserDatasFileGeneration,
        route_name=USER_USERDATAS_PY3O_URL,
        renderer="/userdatas/py3o.mako",
        layout="user",
        context=User,
        permission=PERMISSIONS["global.py3o_userdata"],
    )
    config.add_view(
        TemplatingHistoryDeleteView,
        route_name=TEMPLATING_ITEM_URL,
        request_param="action=delete",
        context=files.TemplatingHistory,
        permission=PERMISSIONS["global.py3o_userdata"],
    )
