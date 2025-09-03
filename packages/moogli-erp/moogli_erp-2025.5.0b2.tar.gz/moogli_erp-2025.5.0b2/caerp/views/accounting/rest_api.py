"""
Accounting rest api

Used to populate the accounting database from desktop tools

"""
import logging
import os
import json
import datetime
from caerp.consts.permissions import PERMISSIONS
from pyramid.security import NO_PERMISSION_REQUIRED
from simplejson import scanner

from caerp.statistics.query_helper import get_query
from caerp.models.company import Company
from caerp.models.accounting.operations import (
    AccountingOperationUpload,
    AccountingOperation,
)
from caerp.utils.rest.apiv1 import Apiv1Resp
from caerp.forms.accounting import get_add_edit_accounting_operation_schema
from caerp.views import BaseRestView

API_ROOT = "/api/v1"
ACCOUNTING_API_ROUTE = os.path.join(API_ROOT, "accounting")
ACCOUNTING_OPERATION_ROUTE = os.path.join(ACCOUNTING_API_ROUTE, "operations")
ACCOUNTING_OPERATION_ITEM_ROUTE = os.path.join(ACCOUNTING_OPERATION_ROUTE, "{id}")


def authentification_check_view(context, request):
    """
    Allows to chek if the accounting authentication is valid without firing any
    additionnal action

    :param obj context: The View's context
    :param obj request: The Pyramid Request object
    """
    return Apiv1Resp(request)


class AccountingOperationRestView(BaseRestView):
    schema = get_add_edit_accounting_operation_schema()
    encodings = ("cp1252", "iso8859-1", "iso8859-16", "utf16", "utf32")

    def __init__(self, *args, **kwargs):
        BaseRestView.__init__(self, *args, **kwargs)
        self.upload_instance_cache = {}
        self.logger.setLevel(logging.INFO)

    def _cache_uploads(self):
        for upload in AccountingOperationUpload.query().filter_by(
            filetype=AccountingOperationUpload.SYNCHRONIZED_ACCOUNTING
        ):
            self.upload_instance_cache[upload.date.year] = upload

    def collection_get(self):
        return AccountingOperation.query().all()

    def _try_solve_encoding_problem(self, request_body):
        """
        :param bytes request_body: Request body as a byte string
        """
        body_unicode_str = "{}"
        for encoding in self.encodings:
            try:
                if isinstance(request_body, bytes):
                    body_unicode_str = request_body.decode(encoding, "strict")
                else:
                    body_unicode_str = request_body
                break
            except UnicodeDecodeError:
                self.logger.exception("Not a {} bytestring".format(encoding))

        try:
            value = json.loads(body_unicode_str, strict=False)
        except json.JSONDecodeError:
            self.logger.exception("Not a valid json string {}".format(body_unicode_str))
            raise
        return value

    def _get_or_create_upload_id(self, date_object):
        """
        Retrieve the AccountingOperationUpload id attached to the given
        date_object's upload

        :param obj date_object: class::`datetime.date` object
        :returns: An AccountingOperationUpload instance
        """
        upload = self.upload_instance_cache.get(date_object.year)
        if upload is None:
            upload = AccountingOperationUpload(
                date=datetime.date(date_object.year, 1, 1),
                filetype=AccountingOperationUpload.SYNCHRONIZED_ACCOUNTING,
                filename="Écritures {}".format(date_object.year),
            )
            self.dbsession.add(upload)
            self.dbsession.flush()
            self.upload_instance_cache[date_object.year] = upload
        else:
            upload.updated_at = datetime.datetime.now()
            self.dbsession.merge(upload)
        return upload.id

    def bulk_post(self):
        """
        Handle bulk insertion of AccountingOperation entries

        expect json body with {'datas': [list of AccountingOperation]}

        Respond to a Http POST request

        E.g:

            Setting:

            caerp.accounting_api_key=06dda91136f6ad4688cdf6c8fd991696

            in the development.ini



            import requests
            from hashlib import md5
            import time

            params = {'datas': [{
                    'analytical_account': "ANALYTICAL",
                    "general_account": "GENERAL",
                    "date": "2018-01-01",
                    'label': "LABEL",
                    "debit": "15",
                    "credit": "15",
                    "balance": "25"
                }]
            }

            def send_post_request(params, api_key):
                timestamp = str(time.time())
                secret = "%s-%s" % (timestamp, api_key)
                encoded = md5(secret.encode('utf-8')).hexdigest()
                url = "http://127.0.0.1:8080/api/v1/accounting/operations"
                headers = {
                    "Authorization" : "HMAC-MD5 %s" % encoded,
                    "Timestamp": timestamp
                }
                resp = requests.post(url, json=params, headers=headers)
                return resp

            resp = send_post_request(
                params,
                "06dda91136f6ad4688cdf6c8fd991696"
            )


        :returns: The inserted entries
        """
        self.logger.debug("POST request (Bulk)")
        self.logger.debug("charset {}".format(self.request.charset))
        self.logger.debug(self.request.body)
        self._cache_uploads()
        result = []
        try:
            json_body = self.request.json_body
            submitted = json_body["datas"]
        except (UnicodeDecodeError, json.JSONDecodeError, scanner.JSONDecodeError):
            self.logger.info("Encoding problem detected, trying to solve automatically")
            try:
                json_body = self._try_solve_encoding_problem(self.request.body)
                submitted = json_body.get("datas", [])
            except Exception as err:
                self.logger.error("Unsolvable encoding error")
                self.logger.error(self.request.body)
                raise err
        except Exception as err:
            self.logger.error("Error while parsing POST data")
            self.logger.error(self.request.body)
            raise err

        for entry in submitted:
            result.append(self._submit_datas(entry))

        self.logger.info(
            "{0} entrie(s) is/are currently added in the database".format(len(result))
        )
        return result

    def post_format(self, entry, edit, attributes):
        """
        Set company id if possible after datas validation and model creation

        :param obj entry: The newly created model
        :param bool edit: Is it edition ?
        :param dict attributes: The validated form attributes
        :returns: The entry
        """
        if "analytical_account" in attributes:
            entry.company_id = Company.get_id_by_analytical_account(
                entry.analytical_account
            )
        entry.upload_id = self._get_or_create_upload_id(entry.date)
        return entry

    def collection_delete(self):
        """
        Handle bulk AccountingOperation deletion

        Respond to a Http DELETE request

        expects json body with filters on the AccountingOperation attributes
        Filters follow a format used in statistics

        e.g:

            import requests
            import time
            params = {'filters': [{'key': 'date', 'type': 'date', 'method':
                'dr', 'search1': '2018-01-01', 'search2': '2018-02-01'}]}

            def send_del_request(params, api_key):
                timestamp = str(time.time())
                secret = "%s-%s" % (timestamp, api_key)
                encoded = md5(secret.encode('utf-8')).hexdigest()
                url = "http://127.0.0.1:8080/api/v1/accounting/operations"
                headers = {
                    "Authorization": "HMAC-MD5 %s" % encoded,
                    "Timestamp": timestamp
                }
                resp = requests.delete(url, json=params, headers=headers)

            send_del_request(
                params,
                "06dda91136f6ad4688cdf6c8fd991696"
            )



        """
        self.logger.info("Bulk AccountingOperation delete")
        filters = self.request.json_body["filters"]
        if "search1" in filters[0]:
            filters[0]["date_search1"] = filters[0]["search1"]
        if "search2" in filters[0]:
            filters[0]["date_search2"] = filters[0]["search2"]
        self.logger.info("    Filters : %s" % filters)

        query = get_query(AccountingOperation, filters)
        self.logger.info("    Deleting {0} entries".format(query.count()))
        for id_, entry in query.all():
            self.request.dbsession.delete(entry)
        return {}


def includeme(config):
    config.add_route(ACCOUNTING_API_ROUTE, ACCOUNTING_API_ROUTE)
    config.add_view(
        authentification_check_view,
        route_name=ACCOUNTING_API_ROUTE,
        request_method="GET",
        request_param="action=check",
        renderer="json",
        permission=NO_PERMISSION_REQUIRED,
        api_key_authentication="caerp.accounting_api_key",
    )
    config.add_route(ACCOUNTING_OPERATION_ROUTE, ACCOUNTING_OPERATION_ROUTE)
    config.add_view(
        AccountingOperationRestView,
        route_name=ACCOUNTING_OPERATION_ROUTE,
        attr="collection_get",
        request_method="GET",
        renderer="json",
        permission=NO_PERMISSION_REQUIRED,
        api_key_authentication="caerp.accounting_api_key",
    )
    config.add_view(
        AccountingOperationRestView,
        route_name=ACCOUNTING_OPERATION_ROUTE,
        attr="bulk_post",
        request_method="POST",
        renderer="json",
        permission=NO_PERMISSION_REQUIRED,
        api_key_authentication="caerp.accounting_api_key",
    )
    config.add_view(
        AccountingOperationRestView,
        route_name=ACCOUNTING_OPERATION_ROUTE,
        attr="collection_delete",
        request_method="DELETE",
        renderer="json",
        permission=NO_PERMISSION_REQUIRED,
        api_key_authentication="caerp.accounting_api_key",
    )
