import uuid
from django.conf import settings
from django.db import models

class CallRecord(models.Model):
    STATUS = [("interested", "Interested"), ("not_interested", "Not Interested"), ("no_answer", "No Answer"),
              ("busy", "Busy"), ("callback", "Call Back Later"), ("wrong_number", "Wrong Number")]
    lead = models.ForeignKey("leads.Lead", on_delete=models.CASCADE, related_name="calls")
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="calls")
    status = models.CharField(max_length=20, choices=STATUS, db_index=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    remarks = models.TextField(blank=True)
    called_at = models.DateTimeField(db_index=True)
    # Idempotency token rendered into the form: a double-submit cannot create two records.
    submit_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["employee", "called_at"])]
        ordering = ["-called_at"]
