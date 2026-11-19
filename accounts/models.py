from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ADMIN, STAFF = "admin", "staff"
    ROLES = [(ADMIN, "Admin"), (STAFF, "Staff")]
    role = models.CharField(max_length=10, choices=ROLES, default=STAFF, db_index=True)
    phone = models.CharField(max_length=15, blank=True)
    employee_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    designation = models.CharField(max_length=60, blank=True)
    daily_target = models.PositiveIntegerField(default=100)
    joined_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_admin_role(self):
        return self.role == self.ADMIN

    def __str__(self):
        return self.get_full_name() or self.username
