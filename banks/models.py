from django.db import models

class Bank(models.Model):
    name = models.CharField(max_length=120, unique=True)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.name

class LoanScheme(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name="schemes")
    name = models.CharField(max_length=120)
    loan_type = models.CharField(max_length=20, default="personal")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="% per annum")
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    min_tenure_months = models.PositiveIntegerField(default=6)
    max_tenure_months = models.PositiveIntegerField(default=60)
    eligibility = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = [("bank", "name")]
    def __str__(self): return f"{self.bank} – {self.name}"
