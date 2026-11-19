import uuid
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from accounts.permissions import staff_required
from call_management.forms import CallForm
from call_management.models import CallRecord
from customers.models import Customer
from followups.models import FollowUp
from leads.models import Lead
from loan_applications.models import LoanApplication
from targets.services import progress
from .ui import list_page, style
from .utils import calls_on, daily_counts

@staff_required
def dashboard(request):
    u, now, today = request.user, timezone.now(), timezone.localdate()
    mine = CallRecord.objects.filter(employee=u)
    labels, data = daily_counts(mine, "called_at", 7)
    fu = FollowUp.objects.filter(employee=u, status="pending")
    apps = LoanApplication.objects.filter(employee=u)
    s = dict(chart_labels=labels, chart_data=data)
    return render(request, "staff/dashboard.html", dict(p=progress(u), s=s, assigned=Lead.objects.filter(assigned_to=u).count(),
        interested=calls_on(mine.filter(status="interested"), today).count(), pending=fu.count(),
        overdue=fu.filter(scheduled_at__lt=now).count(), upcoming=fu.order_by("scheduled_at")[:5],
        apps=apps.count(), approved=apps.filter(status__in=["approved", "disbursed", "closed"]).count()))

@staff_required
def leads(request):
    qs = Lead.objects.filter(assigned_to=request.user)
    return list_page(request, "My Leads", qs, ["Name", "Phone", "City", "Loan", "Amount", "Status"],
        lambda o: {"cells": [o.name, o.phone, o.city, o.get_loan_type_display(), o.loan_amount, o.get_status_display()],
                   "view": reverse("staff_lead", args=[o.pk])},
        ("name", "phone", "city"), [("status", "Status", Lead.STATUS)])

@staff_required
def lead_detail(request, pk):
    u = request.user
    lead = get_object_or_404(Lead, pk=pk, assigned_to=u)           # staff can only open their own leads
    form = CallForm(request.POST or None, initial={"submit_token": uuid.uuid4()})
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        with transaction.atomic():
            call, created = CallRecord.objects.get_or_create(submit_token=d["submit_token"], defaults=dict(
                lead=lead, employee=u, status=d["status"], duration_seconds=d["duration_seconds"] or 0,
                remarks=d["remarks"], called_at=timezone.now()))
            if created:
                if d["status"] in ("interested", "not_interested") and lead.status != "converted":
                    lead.status = d["status"]
                elif d["status"] == "wrong_number":
                    lead.status = "invalid"
                elif lead.status in ("new", "assigned"):
                    lead.status = "contacted"
                lead.save(update_fields=["status", "updated_at"])
                if d["status"] == "interested":
                    Customer.objects.get_or_create(lead=lead, defaults=dict(
                        full_name=lead.name, phone=lead.phone, email=lead.email, city=lead.city,
                        required_amount=lead.loan_amount, loan_requirement=lead.get_loan_type_display() + " loan"))
                if d["followup_at"]:
                    FollowUp.objects.create(lead=lead, employee=u, call=call, scheduled_at=d["followup_at"], notes=d["remarks"][:200])
        messages.success(request, "Call recorded." if created else "This call was already recorded.")
        return redirect("staff_lead", pk=lead.pk)
    return render(request, "staff/lead.html", dict(lead=lead, form=style(form), p=progress(u),
        calls=lead.calls.select_related("employee")[:15], followups=lead.followups.filter(status="pending"),
        customer=Customer.objects.filter(lead=lead).first()))

@staff_required
def loans(request):
    qs = LoanApplication.objects.filter(employee=request.user).select_related("customer", "bank")
    return list_page(request, "My Loan Applications", qs, ["Reference", "Customer", "Bank", "Amount", "Status", "Applied"],
        lambda o: {"cells": [o.reference_no, o.customer, o.bank, o.amount, o.get_status_display(), o.applied_on],
                   "view": reverse("staff_customer", args=[o.customer_id])},
        ("reference_no", "customer__full_name"), [("status", "Status", LoanApplication.STATUS)])
