from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from accounts.permissions import admin_required
from dashboard.ui import form_page, list_page, nsof
from loan_applications.models import LoanApplication
from .forms import DecisionForm
from .models import LoanDecision

@admin_required
def approvals(request):
    ns = nsof(request)
    return list_page(request, "Loan Approvals & Closure", LoanApplication.objects.select_related("customer", "bank", "employee"),
        ["Reference", "Customer", "Bank", "Amount", "Status", "Employee"],
        lambda o: {"cells": [o.reference_no, o.customer, o.bank, o.amount, o.get_status_display(), o.employee],
                   "edit": reverse(ns + "approvals_decide", args=[o.pk])},
        ("reference_no", "customer__full_name"), [("status", "Status", LoanApplication.STATUS)])

@admin_required
def decide(request, pk):
    ns = nsof(request)
    app = get_object_or_404(LoanApplication.objects.select_related("customer__lead", "bank"), pk=pk)
    dec, _ = LoanDecision.objects.get_or_create(application=app)
    form = DecisionForm(request.POST or None, instance=dec)
    if request.method == "POST" and form.is_valid():
        d = form.save(commit=False)
        if d.decision != "pending" and not d.decided_on:
            d.decided_on = timezone.localdate(); d.decided_by = request.user
        d.save()
        app.status = ("closed" if d.closed_on else "disbursed" if d.disbursed_on else "approved" if d.decision == "approved"
                      else "rejected" if d.decision == "rejected" else "under_review")
        app.save(update_fields=["status", "updated_at"])
        if d.decision == "approved":
            lead = app.customer.lead; lead.status = "converted"; lead.save(update_fields=["status", "updated_at"])
        messages.success(request, f"{app.reference_no} updated to {app.get_status_display()}.")
        return redirect(ns + "approvals_list")
    return form_page(request, f"{app.reference_no} · {app.customer} · {app.bank} · ₹{app.amount:.0f}", form, reverse(ns + "approvals_list"))
