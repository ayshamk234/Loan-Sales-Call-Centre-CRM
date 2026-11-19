"""Admin portal routes. Mounted twice: /admin-portal/ (desktop) and /m/ (mobile namespace)."""
from django.urls import path
from banks.urls import urlpatterns as banks
from call_management.urls import urlpatterns as calls
from customers.urls import urlpatterns as customers
from employees.urls import urlpatterns as employees
from followups.urls import urlpatterns as followups
from lead_distribution.urls import urlpatterns as distribution
from leads.urls import urlpatterns as leads
from loan_applications.urls import urlpatterns as applications
from loan_approvals.urls import urlpatterns as approvals
from reports.urls import urlpatterns as reports
from targets.urls import urlpatterns as targets
from documents.views import documents_list
from . import views

urlpatterns = ([path("", views.admin_dashboard, name="dashboard")] + employees + leads + distribution + customers + calls
               + followups + targets + [path("documents/", documents_list, name="documents_list")] + banks
               + applications + approvals + reports)
