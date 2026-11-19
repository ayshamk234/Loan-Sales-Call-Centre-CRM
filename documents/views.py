from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from accounts.permissions import admin_required
from customers.models import Customer
from dashboard.ui import back, list_page, nsof
from .forms import DocumentForm
from .models import Document

def can_access(user, c):
    return user.role == "admin" or c.lead.assigned_to_id == user.id

@login_required
@require_POST
def upload(request, cid):
    c = get_object_or_404(Customer.objects.select_related("lead"), pk=cid)
    if not can_access(request.user, c):
        raise PermissionDenied
    form = DocumentForm(request.POST, request.FILES)
    if form.is_valid():
        d = form.save(commit=False); d.customer = c; d.uploaded_by = request.user; d.save()
        messages.success(request, "Document uploaded. Awaiting admin verification.")
    else:
        messages.error(request, " ".join(e for errs in form.errors.values() for e in errs))
    return back(request, "/")

@admin_required
@require_POST
def verify(request, pk, decision):
    if decision not in ("approved", "rejected"):
        raise Http404
    d = get_object_or_404(Document, pk=pk)
    d.status = decision; d.verified_by = request.user; d.verified_at = timezone.now()
    d.remarks = request.POST.get("remarks", "")[:250]; d.save()
    messages.success(request, f"Document {decision}.")
    return back(request, "/")

@login_required
def file(request, pk):
    d = get_object_or_404(Document.objects.select_related("customer__lead"), pk=pk)
    if not can_access(request.user, d.customer):
        raise PermissionDenied
    return FileResponse(d.file.open("rb"), filename=f"{d.doc_type}_{d.pk}.{d.file.name.rsplit('.', 1)[-1]}")

@admin_required
def documents_list(request):
    ns = nsof(request)
    def row(o):
        return {"cells": [o.customer, o.get_doc_type_display(), o.get_status_display(), o.uploaded_by or "—", o.created_at.strftime("%d %b %Y")],
                "view": reverse("doc_file", args=[o.pk]), "posts": [
                    (reverse("doc_verify", args=[o.pk, "approved"]), "Approve", "success"),
                    (reverse("doc_verify", args=[o.pk, "rejected"]), "Reject", "danger")] if o.status == "pending" else []}
    return list_page(request, "Document Verification", Document.objects.select_related("customer", "uploaded_by"),
        ["Customer", "Type", "Status", "Uploaded by", "Date"], row, ("customer__full_name", "customer__phone"),
        [("status", "Status", Document.STATUS), ("doc_type", "Type", Document.TYPES)])
