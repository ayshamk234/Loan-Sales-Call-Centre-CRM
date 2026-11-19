from django.db.models import Count, Q
from django.urls import path
from django.utils import timezone
from dashboard.ui import crud
from dashboard.utils import day_bounds
from .forms import EmployeeForm
from .models import Employee
from . import views

def qs():
    s, e = day_bounds(timezone.localdate())
    return Employee.objects.filter(role="staff").annotate(
        calls_today=Count("calls", distinct=True, filter=Q(calls__called_at__gte=s, calls__called_at__lt=e)))

def deactivate(u):
    u.is_active = False; u.save()

urlpatterns = crud("employees", Employee, form_class=EmployeeForm, qs=qs, soft_delete=deactivate, title="Employees",
    detail="employee_profile", search=("first_name", "last_name", "username", "employee_code"),
    cols=[("Name", "get_full_name"), ("Code", "employee_code"), ("Username", "username"), ("Phone", "phone"),
          ("Daily target", "daily_target"), ("Calls today", "calls_today"), ("Active", "is_active")]
) + [path("employees/<int:pk>/", views.profile, name="employee_profile")]
