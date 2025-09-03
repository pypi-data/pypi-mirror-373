from .routes import (
    PLAN_ITEM_API_ROUTE,
    CHAPTER_API_ROUTE,
)


def get_progress_invoicing_plan_url(request, plan):
    """
    Build urls used to access progress invoicing plan element

    :rtype: dict
    """
    return dict(
        progress_invoicing_plan_url=request.route_path(PLAN_ITEM_API_ROUTE, id=plan.id),
        progress_invoicing_chapters_url=request.route_path(
            CHAPTER_API_ROUTE,
            id=plan.id,
        ),
    )
