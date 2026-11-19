from accounts.models import User

class Employee(User):
    """Proxy of User for the staff-management module (avoids duplicate tables)."""
    class Meta:
        proxy = True
        ordering = ["first_name"]
