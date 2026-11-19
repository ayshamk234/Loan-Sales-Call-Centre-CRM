from django.urls import path
from customers.views import detail as customer_detail
from followups.views import followups_list
from . import staff, views

urlpatterns = [
    path("", views.home, name="home"),
    path("staff/", staff.dashboard, name="staff_dashboard"),
    path("staff/leads/", staff.leads, name="staff_leads"),
    path("staff/leads/<int:pk>/", staff.lead_detail, name="staff_lead"),
    path("staff/followups/", followups_list, name="staff_followups"),
    path("staff/loans/", staff.loans, name="staff_loans"),
    path("staff/customers/<int:pk>/", customer_detail, name="staff_customer"),
]
