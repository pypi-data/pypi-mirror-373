from .routes import (
    DISCOUNT_API_ROUTE,
    PRICE_STUDY_ITEM_API_ROUTE,
    CHAPTER_API_ROUTE,
)


def get_price_study_api_urls(request, price_study):
    """
    Build urls used to access price_study element

    :rtype: dict
    """
    return dict(
        price_study_url=request.route_path(
            PRICE_STUDY_ITEM_API_ROUTE, id=price_study.id
        ),
        price_study_chapters_url=request.route_path(
            CHAPTER_API_ROUTE,
            id=price_study.id,
        ),
        price_study_discount_api_url=request.route_path(
            DISCOUNT_API_ROUTE, id=price_study.id
        ),
    )
