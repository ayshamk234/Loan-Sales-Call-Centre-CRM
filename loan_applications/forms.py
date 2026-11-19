from django import forms
from accounts.models import User
from .models import LoanApplication

class SchemeRules:
    def clean(self):
        d = super().clean()
        b, s, a, t = d.get("bank"), d.get("scheme"), d.get("amount"), d.get("tenure_months")
        if s:
            if b and s.bank_id != b.pk:
                self.add_error("scheme", "Scheme does not belong to the selected bank.")
            elif a and not (s.min_amount <= a <= s.max_amount):
                self.add_error("amount", f"Amount must be between {s.min_amount:.0f} and {s.max_amount:.0f} for this scheme.")
            if t and not (s.min_tenure_months <= t <= s.max_tenure_months):
                self.add_error("tenure_months", f"Tenure must be {s.min_tenure_months}-{s.max_tenure_months} months.")
        return d

class LoanCreateForm(SchemeRules, forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ["bank", "scheme", "amount", "tenure_months", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 1})}

class LoanAppForm(SchemeRules, forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ["customer", "employee", "bank", "scheme", "amount", "tenure_months", "status", "applied_on", "notes"]
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.fields["employee"].queryset = User.objects.filter(role="staff")
