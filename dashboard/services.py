from django.db.models import Count
from django.utils import timezone
from accounts.models import User
from call_management.models import CallRecord
from followups.models import FollowUp
from leads.models import Lead
from loan_applications.models import LoanApplication
from .utils import daily_counts

DONE = ["approved", "disbursed", "closed"]

def admin_stats(days=7):
    labels, data = daily_counts(CallRecord.objects.all(), "called_at", days)
    st = dict(Lead.objects.values_list("status").annotate(c=Count("id")))
    return {
        "total_leads": Lead.objects.count(),
        "total_employees": User.objects.filter(role="staff", is_active=True).count(),
        "total_calls": CallRecord.objects.count(),
        "interested": Lead.objects.filter(status="interested").count(),
        "pending_followups": FollowUp.objects.filter(status="pending").count(),
        "overdue_followups": FollowUp.objects.filter(status="pending", scheduled_at__lt=timezone.now()).count(),
        "approved_loans": LoanApplication.objects.filter(status__in=DONE).count(),
        "rejected_loans": LoanApplication.objects.filter(status="rejected").count(),
        "chart_labels": labels, "chart_data": data,
        "status_labels": [dict(Lead.STATUS)[k] for k in st], "status_data": list(st.values()),
    }
