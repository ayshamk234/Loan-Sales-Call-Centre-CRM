from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from accounts.permissions import admin_required
from .services import admin_stats

@login_required
def home(request):
    return redirect("dashboard" if request.user.role == "admin" else "staff_dashboard")

@admin_required
def admin_dashboard(request):
    return render(request, "admin/dashboard.html", {"s": admin_stats()})
