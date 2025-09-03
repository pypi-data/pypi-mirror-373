from typing import Optional
from sqlalchemy import select
from caerp.models.project.business import Business
from caerp.models.project.types import BusinessType
from caerp.models.task.invoice import Invoice
from caerp.models.services.bpf import BPFService

from caerp.models.training.bpf import BusinessBPFData


def get_training_businesses_with_invoices_query(start_date, end_date):
    query = (
        select(Business)
        .join(Business.business_type)
        .where(
            BusinessType.bpf_related == True,  # noqa: E712
            Business.invoices_only.any(Invoice.date.between(start_date, end_date)),
        )
    )
    return query


def get_business_bpf_data_query(business_id, financial_year):
    query = select(BusinessBPFData).where(
        BusinessBPFData.business_id == business_id,
        BusinessBPFData.financial_year == financial_year,
    )
    return query


def get_cerfa_spec(year):
    return BPFService.get_spec_from_year(year)


def get_training_goal(year, bpf_data) -> Optional[str]:
    if not bpf_data.training_goal_id:
        return None
    spec = get_cerfa_spec(year)
    training_goals = spec.TRAINING_GOALS
    for id_, cat_name, subcategories in training_goals:
        if id_ is None:
            for subcategory_id, name in subcategories:
                if subcategory_id == bpf_data.training_goal_id:
                    return name
        elif id_ == bpf_data.training_goal_id:
            return cat_name
