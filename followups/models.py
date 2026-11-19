from django.conf import settings
from django.db import models

class FollowUp(models.Model):
    STATUS = [("pending", "Pending"), ("completed", "Completed"), ("cancelled", "Cancelled")]
    lead = models.ForeignKey("leads.Lead", on_delete=models.CASCADE, related_name="followups")
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followups")
    call = models.ForeignKey("call_management.CallRecord", null=True, blank=True, on_delete=models.SET_NULL)
    scheduled_at = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=12, choices=STATUS, default="pending", db_index=True)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["employee", "status", "scheduled_at"])]
        ordering = ["scheduled_at"]
