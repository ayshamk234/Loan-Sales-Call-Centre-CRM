from django.utils import timezone
from call_management.models import CallRecord
from dashboard.utils import calls_on
from .models import DailyTarget

def target_for(user, d):
    t = DailyTarget.objects.filter(employee=user, date=d).first()
    return t.target_calls if t else user.daily_target

def progress(user, d=None):
    d = d or timezone.localdate()
    done = calls_on(CallRecord.objects.filter(employee=user), d).count()
    tg = target_for(user, d)
    pct = round(done * 100 / tg) if tg else 0
    return dict(target=tg, completed=done, remaining=max(tg - done, 0), percent=pct, bar=min(pct, 100))
