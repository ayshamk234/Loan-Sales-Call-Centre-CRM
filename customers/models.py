from django.db import models

class Customer(models.Model):
    EMP = [("salaried", "Salaried"), ("self_employed", "Self Employed"), ("business", "Business Owner"), ("other", "Other")]
    lead = models.OneToOneField("leads.Lead", on_delete=models.PROTECT, related_name="customer")
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=15, db_index=True)
    alt_phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    employment_type = models.CharField(max_length=20, choices=EMP, default="salaried")
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    loan_requirement = models.TextField(blank=True)
    required_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name
