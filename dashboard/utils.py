import datetime
from collections import Counter
from django.utils import timezone

def day_bounds(d):
    s = timezone.make_aware(datetime.datetime.combine(d, datetime.time.min))
    return s, s + datetime.timedelta(days=1)

def parse_date(v, default):
    try:
        return datetime.date.fromisoformat(v)
    except (TypeError, ValueError):
        return default

def calls_on(qs, d, field="called_at"):
    s, e = day_bounds(d)
    return qs.filter(**{field + "__gte": s, field + "__lt": e})

def daily_counts(qs, field, days):
    """Grouped in Python so MySQL timezone tables are NOT required."""
    since = timezone.localdate() - datetime.timedelta(days=days - 1)
    s, _ = day_bounds(since)
    c = Counter(timezone.localtime(v).date() for v in qs.filter(**{field + "__gte": s}).values_list(field, flat=True))
    ds = [since + datetime.timedelta(i) for i in range(days)]
    return [d.strftime("%d %b") for d in ds], [c.get(d, 0) for d in ds]
