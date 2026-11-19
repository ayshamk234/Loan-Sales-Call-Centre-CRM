from dashboard.ui import crud, staff_choices
from .forms import LoanAppForm
from .models import LoanApplication
urlpatterns = crud("applications", LoanApplication, form_class=LoanAppForm, title="Loan Applications",
    qs=lambda: LoanApplication.objects.select_related("customer", "bank", "employee"),
    search=("reference_no", "customer__full_name", "customer__phone"),
    filters=[("status", "Status", LoanApplication.STATUS), ("employee", "Employee", staff_choices)],
    cols=[("Reference", "reference_no"), ("Customer", "customer"), ("Bank", "bank"), ("Amount", "amount"),
          ("Status", "status"), ("Employee", "employee"), ("Applied", "applied_on")])
