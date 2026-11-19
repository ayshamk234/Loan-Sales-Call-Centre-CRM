from dashboard.ui import crud, staff_choices
from .models import CallRecord
urlpatterns = crud("calls", CallRecord, readonly=True, title="Call Records",
    qs=lambda: CallRecord.objects.select_related("lead", "employee"),
    search=("lead__name", "lead__phone", "remarks"),
    filters=[("employee", "Employee", staff_choices), ("status", "Status", CallRecord.STATUS)],
    cols=[("Time", "called_at"), ("Employee", "employee"), ("Lead", "lead.name"), ("Phone", "lead.phone"),
          ("Status", "status"), ("Seconds", "duration_seconds"), ("Remarks", "remarks")])
