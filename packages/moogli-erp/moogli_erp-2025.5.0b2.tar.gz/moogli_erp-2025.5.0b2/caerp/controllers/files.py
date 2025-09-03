import logging

from caerp.models.indicators import SaleFileRequirement

logger = logging.getLogger(__name__)


def copy_files_from_node(request, source, target):
    """
    Copy files from one node to another

    if there a SaleFileRequirement attached to the source node, we copy the file
    and update the target's requirements

    Finally run the file_requirement_service tools if there is one
    """
    for file_object in source.files:
        logger.debug("Copying file %s", file_object.name)
        new_file_object = file_object.duplicate()
        new_file_object.parent = target
        request.dbsession.merge(new_file_object)
        request.dbsession.flush()
        # This one is read only
        target.files.append(new_file_object)

        source_req = (
            SaleFileRequirement.query()
            .filter_by(node_id=source.id)
            .filter_by(file_id=file_object.id)
            .first()
        )
        if source_req:
            logger.debug("Was associated to a requirement %s", source_req.id)
            target_req = SaleFileRequirement.get_by_type_id(
                target.id, source_req.file_type_id
            )
            if target_req and not target_req.file_id:
                logger.debug(
                    "Updating the target requirement %s setting file id %s"
                    % (target_req.id, new_file_object.id),
                )
                target_req.set_file(new_file_object.id)
                request.dbsession.flush()

        if hasattr(target, "file_requirement_service"):
            target.file_requirement_service.register(
                target, new_file_object, action="add"
            )
