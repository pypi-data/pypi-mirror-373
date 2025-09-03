from caerp.models.expense.sheet import ExpenseSheet


def manage_dashboard_expenses_panel(context, request):
    """
    Panel displaying waiting expenses
    """
    # DEPENSES
    expenses = (
        ExpenseSheet.query()
        .filter(ExpenseSheet.status == "wait")
        .order_by(ExpenseSheet.month)
        .order_by(ExpenseSheet.status_date)
        .all()
    )
    for expense in expenses:
        expense.url = request.route_path("/expenses/{id}", id=expense.id)
    return {"expenses": expenses}


def includeme(config):
    config.add_panel(
        manage_dashboard_expenses_panel,
        "manage_dashboard_expenses",
        renderer="caerp:templates/panels/manage/" "manage_dashboard_expenses.mako",
    )
