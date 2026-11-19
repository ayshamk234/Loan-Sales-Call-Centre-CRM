from dashboard.ui import crud
from .models import Bank, LoanScheme
urlpatterns = crud("banks", Bank, title="Banks", search=("name", "contact_person"),
    fields=["name", "contact_person", "phone", "email", "address", "is_active"],
    cols=[("Bank", "name"), ("Contact", "contact_person"), ("Phone", "phone"), ("Email", "email"), ("Active", "is_active")]
) + crud("schemes", LoanScheme, title="Loan Schemes", search=("name", "bank__name"),
    qs=lambda: LoanScheme.objects.select_related("bank"),
    fields=["bank", "name", "loan_type", "interest_rate", "min_amount", "max_amount", "min_tenure_months", "max_tenure_months", "eligibility", "is_active"],
    filters=[("bank", "Bank", lambda: [(b.pk, b.name) for b in Bank.objects.all()])],
    cols=[("Bank", "bank"), ("Scheme", "name"), ("Type", "loan_type"), ("Rate %", "interest_rate"), ("Min", "min_amount"),
          ("Max", "max_amount"), ("Min months", "min_tenure_months"), ("Max months", "max_tenure_months"), ("Active", "is_active")])
