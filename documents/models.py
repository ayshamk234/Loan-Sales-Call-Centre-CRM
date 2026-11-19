import uuid
from django.conf import settings
from django.db import models

def upload_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"documents/{instance.customer_id}/{uuid.uuid4().hex}.{ext}"

class Document(models.Model):
    TYPES = [("aadhaar", "Aadhaar"), ("pan", "PAN"), ("bank_statement", "Bank Statement"),
             ("salary_slip", "Salary Slip"), ("other", "Other")]
    STATUS = [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")]
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=20, choices=TYPES)
    file = models.FileField(upload_to=upload_path)
    status = models.CharField(max_length=10, choices=STATUS, default="pending", db_index=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    verified_at = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
