from caerp.consts.permissions import PERMISSIONS

from .base import BaseSerializer


class CompanySerializer(BaseSerializer):
    acl = {
        "id": PERMISSIONS["global.authenticated"],
        "name": PERMISSIONS["global.authenticated"],
        "goal": PERMISSIONS["global.authenticated"],
        "email": PERMISSIONS["global.authenticated"],
        "mobile": PERMISSIONS["global.authenticated"],
        "phone": PERMISSIONS["global.authenticated"],
        "zip_code": PERMISSIONS["global.authenticated"],
        "latitude": PERMISSIONS["global.authenticated"],
        "longitude": PERMISSIONS["global.authenticated"],
        "users_gallery": PERMISSIONS["global.authenticated"],
        "activities_labels": PERMISSIONS["global.authenticated"],
        "__all__": PERMISSIONS["global.company_view"],
        "customers": PERMISSIONS["global.company_view"],
        "suppliers": PERMISSIONS["global.company_view"],
        "tasks": PERMISSIONS["global.company_view"],
        "invoices": PERMISSIONS["global.company_view"],
        "estimations": PERMISSIONS["global.company_view"],
        "supplier_invoices": PERMISSIONS["global.company_view"],
        "supplier_orders": PERMISSIONS["global.company_view"],
        "projects": PERMISSIONS["global.company_view"],
        "businesses": PERMISSIONS["global.company_view"],
        "employees": PERMISSIONS["global.company_view"],
    }

    exclude_from_children = (
        "node",
        "company",
        "companies",
    )


class CustomerSerializer(BaseSerializer):
    acl = {
        "__all__": PERMISSIONS["company.view"],
    }
    exclude_from_children = ("customer", "customers")


class ProjectSerializer(BaseSerializer):
    acl = {"__all__": PERMISSIONS["company.view"]}
