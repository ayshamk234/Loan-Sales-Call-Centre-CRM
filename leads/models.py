from django.conf import settings
from django.db import models

class Lead(models.Model):
    NEW, ASSIGNED, CONTACTED, INTERESTED, NOT_INTERESTED, CONVERTED, INVALID = (
        "new", "assigned", "contacted", "interested", "not_interested", "converted", "invalid")
    STATUS = [(NEW, "New"), (ASSIGNED, "Assigned"), (CONTACTED, "Contacted"), (INTERESTED, "Interested"),
              (NOT_INTERESTED, "Not Interested"), (CONVERTED, "Converted"), (INVALID, "Invalid")]
    LOAN_TYPES = [("personal", "Personal"), ("home", "Home"), ("business", "Business"),
                  ("vehicle", "Vehicle"), ("education", "Education"), ("other", "Other")]

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=15, unique=True)           # duplicate detection key
    email = models.EmailField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES, default="personal")
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    source = models.CharField(max_length=60, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default=NEW, db_index=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="leads")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                   related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["assigned_to", "status"]), models.Index(fields=["created_at"])]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.phone})"
