from django.conf import settings
from django.db import models

class DailyTarget(models.Model):
    """Target per employee per day. Completed calls are COUNTED from CallRecord, never stored."""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="targets")
    date = models.DateField(db_index=True)
    target_calls = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("employee", "date")]
