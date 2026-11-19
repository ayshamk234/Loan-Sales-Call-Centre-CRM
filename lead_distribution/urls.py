from django.urls import path
from dashboard.ui import crud, staff_choices
from .models import LeadAssignment
from . import views

urlpatterns = [path("distribution/", views.distribute, name="distribute")] + crud(
    "assignments", LeadAssignment, readonly=True, title="Assignment History",
    qs=lambda: LeadAssignment.objects.select_related("lead", "employee", "assigned_by"),
    search=("lead__name", "lead__phone"), filters=[("employee", "Employee", staff_choices), ("mode", "Mode", LeadAssignment.MODES)],
    cols=[("Date", "assigned_on"), ("Lead", "lead.name"), ("Phone", "lead.phone"), ("Employee", "employee"),
          ("Mode", "mode"), ("By", "assigned_by"), ("Active", "is_active"), ("Note", "note")])
