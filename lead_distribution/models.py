from django.conf import settings
from django.db import models

class LeadAssignment(models.Model):
    """History of every assignment / reassignment."""
    MODES = [("manual", "Manual"), ("bulk", "Bulk"), ("auto", "Automatic"), ("reassign", "Reassignment")]
    lead = models.ForeignKey("leads.Lead", on_delete=models.CASCADE, related_name="assignments")
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignments")
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    mode = models.CharField(max_length=10, choices=MODES, default="manual")
    assigned_on = models.DateField(db_index=True)
    is_active = models.BooleanField(default=True)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["employee", "assigned_on"])]
        ordering = ["-created_at"]
    # Only one is_active row per lead is kept by lead_distribution.services.assign()
