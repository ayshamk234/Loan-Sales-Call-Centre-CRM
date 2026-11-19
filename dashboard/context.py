from django.utils import timezone
ADMIN_NAV = [("Dashboard", "dashboard", "bi-speedometer2"), ("Employees", "employees_list", "bi-people"),
    ("Leads", "leads_list", "bi-person-lines-fill"), ("Distribution", "distribute", "bi-shuffle"),
    ("Assignments", "assignments_list", "bi-clock-history"), ("Customers", "customers_list", "bi-person-vcard"),
    ("Call Records", "calls_list", "bi-telephone"), ("Follow-ups", "followups_list", "bi-calendar-check"),
    ("Targets", "targets", "bi-bullseye"), ("Documents", "documents_list", "bi-file-earmark-check"),
    ("Banks", "banks_list", "bi-bank"), ("Loan Schemes", "schemes_list", "bi-percent"),
    ("Applications", "applications_list", "bi-journal-text"), ("Approvals", "approvals_list", "bi-patch-check"),
    ("Reports", "reports", "bi-bar-chart-line")]
STAFF_NAV = [("My Dashboard", "staff_dashboard", "bi-speedometer2"), ("My Leads", "staff_leads", "bi-person-lines-fill"),
    ("Follow-ups", "staff_followups", "bi-calendar-check"), ("Loan Applications", "staff_loans", "bi-journal-text")]

def portal(request):
    u = request.user
    if not u.is_authenticated:
        return {}
    rm = getattr(request, "resolver_match", None)
    ns = "mobile:" if rm and rm.namespace == "mobile" else ""
    ctx = {"ns": ns, "is_mobile": bool(ns), "nav": ADMIN_NAV if u.role == "admin" else STAFF_NAV}
    if u.role == "staff":
        from followups.models import FollowUp
        ctx["due_count"] = FollowUp.objects.filter(employee=u, status="pending",
                                                    scheduled_at__lte=timezone.now() + timezone.timedelta(hours=1)).count()
    return ctx
