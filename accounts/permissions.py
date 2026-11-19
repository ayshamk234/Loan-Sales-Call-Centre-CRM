from functools import wraps
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *a, **kw):
        if not (request.user.is_active and request.user.role == "admin"):
            raise PermissionDenied
        return view(request, *a, **kw)
    return wrapper

def staff_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *a, **kw):
        if request.user.role != "staff":
            raise PermissionDenied
        return view(request, *a, **kw)
    return wrapper

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "admin"

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "staff"
