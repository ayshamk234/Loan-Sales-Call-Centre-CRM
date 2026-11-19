from django.urls import path
from dashboard.ui import crud
from .models import Customer
from . import views
urlpatterns = crud("customers", Customer, add=False, title="Customers", detail="customer_detail",
    form_class=views.CustomerForm, qs=lambda: Customer.objects.select_related("lead"),
    search=("full_name", "phone", "email", "city"),
    cols=[("Name", "full_name"), ("Phone", "phone"), ("City", "city"), ("Employment", "employment_type"),
          ("Income", "monthly_income"), ("Required", "required_amount")]
) + [path("customers/<int:pk>/", views.detail, name="customer_detail")]
