from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from customers.models import Customer
from dashboard.ui import back
from documents.views import can_access
from loan_approvals.models import LoanDecision
from .forms import LoanCreateForm

@login_required
@require_POST
def create(request, cid):
    c = get_object_or_404(Customer.objects.select_related("lead"), pk=cid)
    if not can_access(request.user, c):
        raise PermissionDenied
    form = LoanCreateForm(request.POST)
    if form.is_valid():
        a = form.save(commit=False)
        a.customer = c; a.employee = c.lead.assigned_to or request.user; a.status = "submitted"; a.save()
        LoanDecision.objects.get_or_create(application=a)
        messages.success(request, f"Application {a.reference_no} created.")
    else:
        messages.error(request, " ".join(e for errs in form.errors.values() for e in errs))
    return back(request, "/")
