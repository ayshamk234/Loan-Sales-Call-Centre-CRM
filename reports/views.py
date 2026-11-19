import csv, io
import pandas as pd
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from accounts.models import User
from accounts.permissions import admin_required
from call_management.models import CallRecord
from dashboard.utils import day_bounds, parse_date
from followups.models import FollowUp
from loan_applications.models import LoanApplication

DONE = ["approved", "disbursed", "closed"]

def daily_calls(a, b, df, dt):
    rows = CallRecord.objects.filter(called_at__gte=a, called_at__lt=b).values_list(
        "called_at", "employee__first_name", "employee__last_name", "status", "duration_seconds")
    cols = ["Date", "Employee", "Calls", "Interested", "Not interested", "No answer", "Busy", "Avg duration (s)"]
    d = pd.DataFrame(list(rows), columns=["t", "f", "l", "s", "dur"])
    if d.empty:
        return cols, []
    d["Date"] = d.t.map(lambda x: timezone.localtime(x).date().isoformat()); d["Employee"] = (d.f + " " + d.l).str.strip()
    g = d.groupby(["Date", "Employee"])
    out = pd.DataFrame({"Calls": g.size(), **{n: g.s.apply(lambda x, k=k: int((x == k).sum())) for n, k in
           [("Interested", "interested"), ("Not interested", "not_interested"), ("No answer", "no_answer"), ("Busy", "busy")]},
           "Avg": g.dur.mean().round()}).reset_index()
    return cols, out[["Date", "Employee", "Calls", "Interested", "Not interested", "No answer", "Busy", "Avg"]].values.tolist()

def employee_perf(a, b, df, dt):
    days = (dt - df).days + 1
    qs = User.objects.filter(role="staff").annotate(
        ncalls=Count("calls", distinct=True, filter=Q(calls__called_at__gte=a, calls__called_at__lt=b)),
        interested=Count("calls", distinct=True, filter=Q(calls__called_at__gte=a, calls__called_at__lt=b, calls__status="interested")),
        fdone=Count("followups", distinct=True, filter=Q(followups__status="completed", followups__completed_at__gte=a, followups__completed_at__lt=b)),
        apps=Count("applications", distinct=True, filter=Q(applications__applied_on__range=(df, dt))),
        ok=Count("applications", distinct=True, filter=Q(applications__applied_on__range=(df, dt), applications__status__in=DONE)))
    cols = ["Employee", "Calls", "Interested", "Follow-ups done", "Applications", "Approved", "Target achievement %"]
    return cols, [[str(u), u.ncalls, u.interested, u.fdone, u.apps, u.ok,
                   round(u.ncalls * 100 / (u.daily_target * days)) if u.daily_target else 0] for u in qs]

def lead_conversion(a, b, df, dt):
    qs = User.objects.filter(role="staff").annotate(n=Count("leads", distinct=True),
        i=Count("leads", distinct=True, filter=Q(leads__status="interested")),
        c=Count("leads", distinct=True, filter=Q(leads__status="converted")))
    return (["Employee", "Leads held", "Interested", "Converted", "Conversion %"],
            [[str(u), u.n, u.i, u.c, round(u.c * 100 / u.n) if u.n else 0] for u in qs])

def loan_approvals(a, b, df, dt):
    qs = LoanApplication.objects.filter(applied_on__range=(df, dt)).select_related("customer", "bank", "employee", "decision")
    def dec(x, f):
        d = getattr(x, "decision", None); return getattr(d, f, "") or ""
    return (["Reference", "Customer", "Bank", "Employee", "Amount", "Status", "Approved amt", "Disbursed on"],
            [[x.reference_no, str(x.customer), str(x.bank), str(x.employee), float(x.amount), x.get_status_display(),
              float(dec(x, "approved_amount") or 0), str(dec(x, "disbursed_on"))] for x in qs])

def followups(a, b, df, dt):
    qs = FollowUp.objects.filter(scheduled_at__gte=a, scheduled_at__lt=b).select_related("lead", "employee")
    now = timezone.now()
    return (["Lead", "Phone", "Employee", "Scheduled", "Status"],
            [[f.lead.name, f.lead.phone, str(f.employee), timezone.localtime(f.scheduled_at).strftime("%Y-%m-%d %H:%M"),
              "Overdue" if f.status == "pending" and f.scheduled_at < now else f.get_status_display()] for f in qs])

REPORTS = {"daily_calls": ("Daily call report", daily_calls), "employee_perf": ("Employee performance", employee_perf),
           "lead_conversion": ("Lead conversion (all-time)", lead_conversion), "loan_approvals": ("Loan approvals", loan_approvals),
           "followups": ("Follow-ups", followups)}

@admin_required
def reports(request):
    kind = request.GET.get("report", "daily_calls")
    kind = kind if kind in REPORTS else "daily_calls"
    today = timezone.localdate()
    df = parse_date(request.GET.get("from"), today - timezone.timedelta(days=6)); dt = parse_date(request.GET.get("to"), today)
    a, _ = day_bounds(df); _, b = day_bounds(dt)
    cols, rows = REPORTS[kind][1](a, b, df, dt)
    fmt = request.GET.get("export")
    if fmt == "csv":
        r = HttpResponse(content_type="text/csv"); r["Content-Disposition"] = f'attachment; filename="{kind}.csv"'
        w = csv.writer(r); w.writerow(cols); w.writerows(rows); return r
    if fmt == "xlsx":
        buf = io.BytesIO(); pd.DataFrame(rows, columns=cols).to_excel(buf, index=False)
        r = HttpResponse(buf.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        r["Content-Disposition"] = f'attachment; filename="{kind}.xlsx"'; return r
    return render(request, "admin/reports.html", dict(kind=kind, reports=[(k, v[0]) for k, v in REPORTS.items()], cols=cols,
                  rows=rows, df=df, dt=dt, title=REPORTS[kind][0]))
