from django import forms
from .models import LoanDecision

class DecisionForm(forms.ModelForm):
    class Meta:
        model = LoanDecision
        fields = ["decision", "approved_amount", "rejection_reason", "disbursed_amount", "disbursed_on", "closed_on", "remarks"]
        widgets = {"remarks": forms.Textarea(attrs={"rows": 2})}
    def clean(self):
        d = super().clean()
        if d.get("decision") == "rejected" and not d.get("rejection_reason"):
            self.add_error("rejection_reason", "Give a reason for rejection.")
        if d.get("decision") == "approved" and not d.get("approved_amount"):
            self.add_error("approved_amount", "Enter the approved amount.")
        if d.get("disbursed_on") and d.get("decision") != "approved":
            self.add_error("disbursed_on", "Only approved loans can be disbursed.")
        if d.get("closed_on") and not d.get("disbursed_on"):
            self.add_error("closed_on", "Disburse the loan before closing it.")
        return d
