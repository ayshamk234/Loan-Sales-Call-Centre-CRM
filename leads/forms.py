import re
from django import forms
from .models import Lead

def clean_phone(raw):
    d = re.sub(r"\D", "", str(raw or ""))[-10:]
    return d if len(d) == 10 and d[0] in "6789" else None

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["name", "phone", "email", "city", "loan_type", "loan_amount", "source", "status"]
    def clean_phone(self):
        p = clean_phone(self.cleaned_data["phone"])
        if not p:
            raise forms.ValidationError("Enter a valid 10-digit Indian mobile number.")
        return p

class UploadForm(forms.Form):
    file = forms.FileField(label="CSV or Excel file")
    def clean_file(self):
        f = self.cleaned_data["file"]
        if not f.name.lower().endswith((".csv", ".xlsx", ".xls")):
            raise forms.ValidationError("Upload a .csv, .xlsx or .xls file.")
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File must be 5 MB or smaller.")
        return f
