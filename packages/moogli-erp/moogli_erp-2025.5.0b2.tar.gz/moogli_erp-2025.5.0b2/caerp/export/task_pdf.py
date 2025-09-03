import io
import logging

from PyPDF4 import PdfFileReader, PdfFileWriter
from PyPDF4.generic import Destination

from caerp.interfaces import ITaskPdfRenderingService, ITaskPdfStorageService
from caerp.models.task import Task
from caerp.utils.pdf import (
    HTMLWithHeadersAndFooters,
    Overlay,
    fetch_resource,
    weasyprint_pdf_css,
)

logger = logging.getLogger(__name__)


def _pdf_renderer(task, request, with_cgv=True):
    footer = Overlay(
        panel_name="task_pdf_footer",
        context_dict={"context": task},
    )
    content = request.layout_manager.render_panel(
        "task_pdf_content", context=task, with_cgv=with_cgv
    )
    html_object = HTMLWithHeadersAndFooters(
        request,
        content,
        footer_overlay=footer,
        url_fetcher=fetch_resource,
        base_url="test",
    )
    return html_object


def task_pdf(task, request):
    """
    Generates the pdf output for a given task

    :rtype: io.BytesIO instance
    """
    result = io.BytesIO()
    html_object = _pdf_renderer(task, request)
    html_object.write_pdf(result, stylesheets=weasyprint_pdf_css())
    result.seek(0)
    return result


# Fonctions relatives à l'Export massif
def _get_pages_without_cgv(pdf_reader):
    """
    return A Pdf buffer with the task pdf datas without cgv

    :param obj pdf_reader: a PdfFileReader instance
    """
    cgv_outline = None
    for outline in pdf_reader.getOutlines():
        if isinstance(outline, Destination):
            if outline.title == "CGV":
                cgv_outline = outline
                break

    if cgv_outline is not None:
        cgv_page_number = pdf_reader.getDestinationPageNumber(outline)
        return pdf_reader.pages[0:cgv_page_number]

    else:
        return pdf_reader.pages


def task_bulk_pdf(tasks, request):
    """
    Produce a pdf containing merged tasks pdf

    :param list tasks: list of Task objects
    """
    logger.debug("In task_bulk_pdf")
    logger.debug(tasks)
    storage_factory = request.find_service_factory(ITaskPdfStorageService, context=Task)
    storage_engine = storage_factory(None, request)
    renderer_factory = request.find_service_factory(
        ITaskPdfRenderingService, context=Task
    )
    render_engine = renderer_factory(None, request)

    pdf_writer = PdfFileWriter()
    for task in tasks:
        storage_engine.set_task(task)
        pdf_buffer = storage_engine.retrieve_pdf()

        if not pdf_buffer:
            render_engine.set_task(task)
            pdf_buffer = render_engine.render()
            filename = render_engine.filename()
            storage_engine.store_pdf(filename, pdf_buffer)
            pdf_buffer.seek(0)
        else:
            logger.debug("PDF BUFFER Was not None")

        reader = PdfFileReader(pdf_buffer)
        for page in _get_pages_without_cgv(reader):
            pdf_writer.addPage(page)

    result = io.BytesIO()
    pdf_writer.write(result)
    return result


def ensure_task_pdf_persisted(task, request):
    """
    Persist a task's pdf if it's not done yet

    :returns: A buffer with the pdf data
    :rtype: IO-like buffer
    """
    storage_service = request.find_service(
        ITaskPdfStorageService,
        context=task,
    )

    pdf_buffer = storage_service.retrieve_pdf()

    if pdf_buffer is None:
        logger.info(
            "The PDF of the task {} has not been persisted on disk "
            "yet".format(task.id)
        )
        rendering_service = request.find_service(
            ITaskPdfRenderingService,
            context=task,
        )

        filename = rendering_service.filename()
        pdf_buffer = rendering_service.render()
        pdf_buffer = storage_service.store_pdf(filename, pdf_buffer)

    return pdf_buffer
