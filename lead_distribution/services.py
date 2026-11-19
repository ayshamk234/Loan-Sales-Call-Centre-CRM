from django.db import transaction
from django.utils import timezone
from leads.models import Lead
from .models import LeadAssignment

def unassigned():
    return Lead.objects.filter(assigned_to__isnull=True, status="new").order_by("created_at", "pk")

def assign(ids, employee, by, mode, note=""):
    ids = list(ids)
    with transaction.atomic():
        LeadAssignment.objects.filter(lead_id__in=ids, is_active=True).update(is_active=False)
        LeadAssignment.objects.bulk_create([LeadAssignment(lead_id=i, employee=employee, assigned_by=by, mode=mode,
                                           assigned_on=timezone.localdate(), note=note) for i in ids])
        Lead.objects.filter(pk__in=ids).update(assigned_to=employee)
        Lead.objects.filter(pk__in=ids, status="new").update(status="assigned")
    return len(ids)
