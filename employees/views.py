from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from accounts.permissions import admin_required
from call_management.models import CallRecord
from dashboard.utils import daily_counts
from targets.services import progress
from .models import Employee

@admin_required
def profile(request, pk):
    e = get_object_or_404(Employee, pk=pk, role="staff")
    calls = CallRecord.objects.filter(employee=e)
    labels, data = daily_counts(calls, "called_at", 7)
    total = calls.count(); intr = calls.filter(status="interested").count()
    stats = dict(total_calls=total, interested=intr, rate=round(intr * 100 / total) if total else 0,
                 leads=e.leads.count(), pending_followups=e.followups.filter(status="pending").count(),
                 applications=e.applications.count(),
                 approved=e.applications.filter(status__in=["approved", "disbursed", "closed"]).count())
    return render(request, "admin/employee_profile.html", dict(e=e, stats=stats, p=progress(e),
                  s={"chart_labels": labels, "chart_data": data}))
