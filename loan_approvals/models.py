from django.conf import settings
from django.db import models

class LoanDecision(models.Model):
    DECISION = [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")]
    application = models.OneToOneField("loan_applications.LoanApplication", on_delete=models.CASCADE, related_name="decision")
    decision = models.CharField(max_length=10, choices=DECISION, default="pending", db_index=True)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    decided_on = models.DateField(null=True, blank=True)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rejection_reason = models.CharField(max_length=250, blank=True)
    disbursed_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    disbursed_on = models.DateField(null=True, blank=True)
    closed_on = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
