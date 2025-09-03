"""
Panel related to PDF rendering of activities


The page is constructed with a content and a footer

Content is a full html page (enclosed in <html></html>

Footer is added through our utils.pdf.HTMLWithHeaderAndFooter weasyprint
utility class

"""
from caerp.models.config import ConfigFiles
from caerp.models.user.userdatas import AntenneOption


def pdf_header_panel(context, request):
    """
    The panel used to render the header of the pdf content
    """
    header_key = "workshop_header_img.png"

    has_header = ConfigFiles.query().filter_by(key=header_key).count() > 0
    return dict(has_header=has_header, url="/public/{}".format(header_key))


def pdf_content_panel(context, request, timeslots):
    """
    The panel used to render the workshop as a PDF

    :param obj context: The current workshop
    """
    antenna_count = AntenneOption.query().count()
    return dict(
        workshop=context,
        timeslots=timeslots,
        participants=context.sorted_participants,
        is_multi_antenna_server=antenna_count > 1,
    )


def pdf_footer_panel(context, request, **kwargs):
    """
    The panel used to render the workshop pdf footer

    :param obj context: The current workshop
    """
    img_key = "workshop_footer_img.png"
    has_img = ConfigFiles.query().filter_by(key=img_key).count() > 0
    text = request.config.get("workshop_footer")
    return dict(
        img_url="/public/{}".format(img_key),
        has_img=has_img,
        text=text,
        has_text=bool(text),
        **kwargs,
    )


def includeme(config):
    config.add_panel(
        pdf_header_panel,
        "workshop_pdf_header",
        renderer="panels/workshop/pdf_header.mako",
    )
    config.add_panel(
        pdf_content_panel,
        "workshop_pdf_content",
        renderer="panels/workshop/pdf_content.mako",
    )
    config.add_panel(
        pdf_footer_panel,
        "workshop_pdf_footer",
        renderer="panels/workshop/pdf_footer.mako",
    )
