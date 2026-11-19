from django.urls import path
from dashboard.ui import crud, staff_choices
from .forms import LeadForm
from .models import Lead
from . import views

def on_save(o, request, created):
    if created:
        o.created_by = request.user

urlpatterns = crud("leads", Lead, form_class=LeadForm, on_save=on_save, title="Leads", extra=[("Bulk upload", "leads_upload")],
    qs=lambda: Lead.objects.select_related("assigned_to"),
    search=("name", "phone", "city", "email"),
    filters=[("status", "Status", Lead.STATUS), ("assigned_to", "Employee", staff_choices), ("loan_type", "Loan", Lead.LOAN_TYPES)],
    cols=[("Name", "name"), ("Phone", "phone"), ("City", "city"), ("Loan", "loan_type"), ("Amount", "loan_amount"),
          ("Status", "status"), ("Assigned to", "assigned_to")]
) + [path("leads/upload/", views.upload, name="leads_upload"), path("leads/sample.csv", views.sample, name="leads_sample")]
