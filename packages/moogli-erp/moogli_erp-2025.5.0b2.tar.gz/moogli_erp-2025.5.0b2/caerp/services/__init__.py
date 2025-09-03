from sqlalchemy import select


def get_model_by_id(request, model, model_id):
    """Retrieve a model by its ID"""
    query = select(model).where(model.id == model_id)
    return request.dbsession.execute(query).scalar_one_or_none()
