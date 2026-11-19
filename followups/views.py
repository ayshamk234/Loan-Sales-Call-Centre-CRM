from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from dashboard.ui import back, list_page
from .models import FollowUp

@login_required
def followups_list(request):
    u, now = request.user, timezone.now()
    qs = FollowUp.objects.select_related("lead", "employee")
    if u.role == "staff":
        qs = qs.filter(employee=u)
    tab = request.GET.get("tab", "pending")
    qs = {"pending": qs.filter(status="pending"), "overdue": qs.filter(status="pending", scheduled_at__lt=now),
          "completed": qs.filter(status="completed")}.get(tab, qs)
    def row(o):
        st = "Overdue" if o.status == "pending" and o.scheduled_at < now else o.get_status_display()
        r = {"cells": [o.lead.name, o.lead.phone, o.employee, timezone.localtime(o.scheduled_at).strftime("%d %b %Y %H:%M"), st, o.notes],
             "posts": [(reverse("followup_done", args=[o.pk]), "Complete", "success")] if o.status == "pending" else []}
        if u.role == "staff":
            r["view"] = reverse("staff_lead", args=[o.lead_id])
        return r
    tabs = [(t.title(), f"{request.path}?tab={t}") for t in ("pending", "overdue", "completed", "all")]
    return list_page(request, "Follow-ups", qs.order_by("scheduled_at"), ["Lead", "Phone", "Employee", "Scheduled", "Status", "Notes"],
                     row, ("lead__name", "lead__phone"), extra=tabs, keep=("tab",))

@login_required
@require_POST
def done(request, pk):
    f = get_object_or_404(FollowUp, pk=pk)
    if request.user.role != "admin" and f.employee_id != request.user.id:
        raise PermissionDenied
    f.status = "completed"; f.completed_at = timezone.now(); f.save()
    messages.success(request, "Follow-up marked complete.")
    return back(request, "/")
