import logging
from caerp.models.indicators import SaleFileRequirement

from caerp.utils.controller import BaseAddEditController
from caerp.events.indicators import IndicatorChanged
from caerp.utils.rest.parameters import LoadOptions


logger = logging.getLogger(__name__)


class IndicatorController(BaseAddEditController):
    def collection_get(self, params: LoadOptions) -> list:
        """
        Return The file requirements attached to the given node
        """
        if hasattr(self.context, "get_file_requirements"):
            scoped = params.filters and "scoped" in params.filters

            # Collect the file requirements attached to business/tasks/projects
            result = self.context.get_file_requirements(scoped=scoped)
        else:
            result = self.context.file_requirements
        return result

    def force(self) -> SaleFileRequirement:
        if self.context.forced:
            self.context.unforce()
            logger.debug(
                "+ Setting force=False for the indicator {}".format(
                    self.context.id,
                )
            )
        else:
            logger.debug(
                "+ Setting force=True for the indicator {}".format(
                    self.context.id,
                )
            )
            self.context.force()
        self.request.dbsession.merge(self.context)
        self.request.registry.notify(IndicatorChanged(self.request, self.context))
        return self.context

    def validate(self, validation_status: str) -> SaleFileRequirement:
        if validation_status in self.context.VALIDATION_STATUS:
            logger.debug(
                "+ Setting the status of the indicator {} to {}".format(
                    self.context.id, validation_status
                )
            )
            self.context.set_validation_status(validation_status)
            self.request.registry.notify(IndicatorChanged(self.request, self.context))
        else:
            self.request.session.flash("Statut invalide : %s" % validation_status)
        return self.context
