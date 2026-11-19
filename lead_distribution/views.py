from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from accounts.models import User
from accounts.permissions import admin_required
from dashboard.ui import nsof
from leads.models import Lead
from .services import assign, unassigned

@admin_required
def distribute(request):
    staff = User.objects.filter(role="staff", is_active=True)
    if request.method == "POST":
        a, by = request.POST.get("action"), request.user
        try:
            if a == "manual":
                emp = get_object_or_404(staff, pk=request.POST.get("employee"))
                ids = Lead.objects.filter(pk__in=request.POST.getlist("leads")).values_list("pk", flat=True)
                msg = f"{assign(ids, emp, by, 'manual')} leads assigned to {emp}."
            elif a == "bulk":
                emp = get_object_or_404(staff, pk=request.POST.get("employee"))
                n = int(request.POST.get("count") or 0)
                msg = f"{assign(unassigned().values_list('pk', flat=True)[:n], emp, by, 'bulk')} leads assigned to {emp}."
            elif a == "auto":
                emps = list(staff.filter(pk__in=request.POST.getlist("employees")))
                cap = int(request.POST.get("cap") or 100)
                if not emps:
                    raise ValueError("Select at least one employee.")
                pool = list(unassigned().values_list("pk", flat=True)[:cap * len(emps)])
                buckets = {e.pk: [] for e in emps}
                for i, lid in enumerate(pool):
                    buckets[emps[i % len(emps)].pk].append(lid)
                for e in emps:
                    assign(buckets[e.pk], e, by, "auto")
                msg = f"{len(pool)} leads distributed across {len(emps)} employees."
            elif a == "reassign":
                frm = get_object_or_404(User, pk=request.POST.get("from_emp"), role="staff")
                to = get_object_or_404(staff, pk=request.POST.get("to_emp"))
                if frm == to:
                    raise ValueError("Choose two different employees.")
                qs = Lead.objects.filter(assigned_to=frm, status__in=["assigned", "contacted"]).order_by("pk")
                n = int(request.POST.get("count") or 0)
                ids = list(qs.values_list("pk", flat=True)[:n] if n else qs.values_list("pk", flat=True))
                msg = f"{assign(ids, to, by, 'reassign', f'From {frm}')} leads moved from {frm} to {to}."
            else:
                raise ValueError("Unknown action.")
            messages.success(request, msg)
        except (ValueError, TypeError) as ex:
            messages.error(request, str(ex) or "Invalid input.")
        return redirect(nsof(request) + "distribute")
    today = timezone.localdate()
    staff = staff.annotate(today_assigned=Count("assignments", distinct=True, filter=Q(assignments__assigned_on=today, assignments__is_active=True)),
                           active_leads=Count("leads", distinct=True))
    return render(request, "admin/distribute.html", dict(staff=staff, unassigned_count=unassigned().count(),
                  sample=unassigned()[:100]))
