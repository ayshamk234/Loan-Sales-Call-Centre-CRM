import pandas as pd
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from accounts.permissions import admin_required
from dashboard.ui import style
from .forms import UploadForm, clean_phone
from .models import Lead

ALIASES = {"mobile": "phone", "phone_number": "phone", "contact": "phone", "mobile_number": "phone",
           "full_name": "name", "customer_name": "name", "amount": "loan_amount", "loan": "loan_type", "type": "loan_type"}
TYPES = {k for k, _ in Lead.LOAN_TYPES}

@admin_required
def upload(request):
    form = UploadForm(request.POST or None, request.FILES or None)
    result = None
    if request.method == "POST" and form.is_valid():
        f = form.cleaned_data["file"]
        try:
            df = pd.read_csv(f, dtype=str) if f.name.lower().endswith(".csv") else pd.read_excel(f, dtype=str)
        except Exception:
            messages.error(request, "Could not read the file. Check the format.")
            df = None
        if df is not None:
            df.columns = [ALIASES.get(c.strip().lower().replace(" ", "_"), c.strip().lower().replace(" ", "_")) for c in df.columns]
            if not {"name", "phone"} <= set(df.columns):
                messages.error(request, "File must contain 'name' and 'phone' columns.")
            elif len(df) > 5000:
                messages.error(request, "Maximum 5000 rows per upload.")
            else:
                existing = set(Lead.objects.values_list("phone", flat=True))
                new, seen, dup, bad = [], set(), 0, []
                for i, r in df.fillna("").iterrows():
                    ph = clean_phone(r["phone"]); nm = str(r["name"]).strip()
                    if not nm or not ph:
                        bad.append(f"Row {i + 2}: invalid name/phone"); continue
                    if ph in existing or ph in seen:
                        dup += 1; continue
                    seen.add(ph)
                    try:
                        amt = Decimal(str(r.get("loan_amount", "")).replace(",", "")) if r.get("loan_amount") else None
                    except InvalidOperation:
                        amt = None
                    lt = str(r.get("loan_type", "")).strip().lower()
                    new.append(Lead(name=nm[:120], phone=ph, email=str(r.get("email", ""))[:254], city=str(r.get("city", ""))[:80],
                                    loan_type=lt if lt in TYPES else "other" if lt else "personal", loan_amount=amt,
                                    source=str(r.get("source", "")) or "Bulk upload", created_by=request.user))
                Lead.objects.bulk_create(new, batch_size=500, ignore_conflicts=True)
                result = dict(total=len(df), added=len(new), duplicates=dup, invalid=len(bad), errors=bad[:20])
                messages.success(request, f"{len(new)} leads imported, {dup} duplicates skipped.")
    return render(request, "admin/lead_upload.html", dict(form=style(form), result=result))

@admin_required
def sample(request):
    r = HttpResponse("name,phone,email,city,loan_type,loan_amount,source\nAnil Nair,9876501234,anil@example.com,Kochi,personal,300000,Facebook\n",
                     content_type="text/csv")
    r["Content-Disposition"] = 'attachment; filename="sample_leads.csv"'
    return r
