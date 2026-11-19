from django.conf import settings
from django.db import models
from django.utils import timezone

class LoanApplication(models.Model):
    STATUS = [("draft", "Draft"), ("submitted", "Submitted to Bank"), ("under_review", "Under Review"),
              ("approved", "Approved"), ("rejected", "Rejected"), ("disbursed", "Disbursed"), ("closed", "Closed")]
    reference_no = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey("customers.Customer", on_delete=models.PROTECT, related_name="applications")
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="applications")
    bank = models.ForeignKey("banks.Bank", on_delete=models.PROTECT, related_name="applications")
    scheme = models.ForeignKey("banks.LoanScheme", null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure_months = models.PositiveIntegerField(default=12)
    status = models.CharField(max_length=15, choices=STATUS, default="draft", db_index=True)
    applied_on = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *a, **kw):
        if not self.reference_no:
            import uuid
            self.reference_no = uuid.uuid4().hex[:20]       # temporary, replaced below
            super().save(*a, **kw)
            self.reference_no = f"LN{timezone.now():%y%m}{self.pk:06d}"
            return super().save(update_fields=["reference_no"])
        super().save(*a, **kw)
