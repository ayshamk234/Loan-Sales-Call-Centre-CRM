from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import Employee

class EmployeeForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput(render_value=False),
                               help_text="Required for new employees; leave blank to keep the current one.")
    class Meta:
        model = Employee
        fields = ["username", "first_name", "last_name", "email", "phone", "employee_code", "designation",
                  "daily_target", "joined_on", "is_active"]
    def clean_password(self):
        pw = self.cleaned_data["password"]
        if not self.instance.pk and not pw:
            raise forms.ValidationError("Password is required for a new employee.")
        if pw:
            validate_password(pw)
        return pw
    def save(self, commit=True):
        u = super().save(commit=False)
        u.role = "staff"
        if self.cleaned_data["password"]:
            u.set_password(self.cleaned_data["password"])
        if commit:
            u.save()
        return u
