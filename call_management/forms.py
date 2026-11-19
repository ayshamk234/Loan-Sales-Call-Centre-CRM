from django import forms
from django.utils import timezone
from .models import CallRecord

class CallForm(forms.ModelForm):
    followup_at = forms.DateTimeField(required=False, label="Schedule follow-up (optional)")
    submit_token = forms.UUIDField(widget=forms.HiddenInput)
    class Meta:
        model = CallRecord
        fields = ["status", "duration_seconds", "remarks"]
        labels = {"duration_seconds": "Duration (seconds)"}
    def clean_followup_at(self):
        v = self.cleaned_data.get("followup_at")
        if v and v <= timezone.now():
            raise forms.ValidationError("Follow-up must be scheduled in the future.")
        return v
