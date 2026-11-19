from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from accounts.models import User
from accounts.permissions import admin_required
from dashboard.ui import nsof
from dashboard.utils import parse_date
from .models import DailyTarget
from .services import progress

@admin_required
def targets(request):
    d = parse_date(request.GET.get("date"), timezone.localdate())
    if request.method == "POST":
        try:
            emp = User.objects.get(pk=request.POST["employee"], role="staff")
            n = int(request.POST["target"]); assert 0 < n <= 1000
            DailyTarget.objects.update_or_create(employee=emp, date=d, defaults={"target_calls": n})
            messages.success(request, f"Target for {emp} set to {n}.")
        except Exception:
            messages.error(request, "Invalid target value.")
        return redirect(f"{request.path}?date={d}")
    rows = [(u, progress(u, d)) for u in User.objects.filter(role="staff", is_active=True).order_by("first_name")]
    tot_t = sum(p["target"] for _, p in rows); tot_c = sum(p["completed"] for _, p in rows)
    return render(request, "admin/targets.html", dict(rows=rows, d=d, tot_t=tot_t, tot_c=tot_c,
                  tot_pct=round(tot_c * 100 / tot_t) if tot_t else 0))
