from django import template
register = template.Library()
OK = {"approved", "disbursed", "closed", "completed", "interested", "converted"}
BAD = {"rejected", "not interested", "overdue", "invalid", "wrong number", "cancelled"}
INFO = {"submitted to bank", "under review", "assigned", "contacted", "submitted"}
@register.filter
def badge(v):
    v = str(v).lower()
    return "success" if v in OK else "danger" if v in BAD else "info" if v in INFO else "warning"
