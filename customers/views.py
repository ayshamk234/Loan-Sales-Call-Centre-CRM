from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from dashboard.ui import back, form_page, nsof, style
from documents.forms import DocumentForm
from documents.views import can_access
from loan_applications.forms import LoanCreateForm
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ["lead", "created_at", "updated_at"]

@login_required
def detail(request, pk):
    c = get_object_or_404(Customer.objects.select_related("lead", "lead__assigned_to"), pk=pk)
    if not can_access(request.user, c):
        raise PermissionDenied
    return render(request, "base/customer_detail.html", dict(
        c=c, calls=c.lead.calls.select_related("employee")[:20], followups=c.lead.followups.select_related("employee")[:20],
        docs=c.documents.select_related("uploaded_by"), apps=c.applications.select_related("bank", "employee"),
        doc_form=style(DocumentForm()), loan_form=style(LoanCreateForm())))

@login_required
def edit(request, pk):
    c = get_object_or_404(Customer.objects.select_related("lead"), pk=pk)
    if not can_access(request.user, c):
        raise PermissionDenied
    form = CustomerForm(request.POST or None, instance=c)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Customer updated.")
        return back(request, "/")
    return form_page(request, f"Edit {c.full_name}", form, request.GET.get("next") or "/")
