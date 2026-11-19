import random
from datetime import timedelta
from decimal import Decimal
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from banks.models import Bank, LoanScheme
from call_management.models import CallRecord
from customers.models import Customer
from documents.models import Document
from followups.models import FollowUp
from lead_distribution.services import assign
from leads.models import Lead
from loan_applications.models import LoanApplication
from loan_approvals.models import LoanDecision

FIRST = "Anil Bindu Cyril Deepa Eldho Fathima Gopan Hari Indu Jibin Kavya Libin Meera Nikhil Omana Pradeep Rekha Sanju".split()
LAST = "Nair Thomas Joseph Menon Varghese Pillai Kurian Das George Mathew".split()
CITY = ["Kochi", "Thrissur", "Kozhikode", "Kollam", "Palakkad"]

class Command(BaseCommand):
    help = "Create demo users and FICTIONAL sample data (idempotent)."
    def handle(self, *a, **kw):
        admin, _ = User.objects.get_or_create(username="admin", defaults=dict(email="admin@example.com", first_name="Asha", last_name="Menon",
                                              role="admin", is_staff=True, is_superuser=True, employee_code="EMP000"))
        admin.set_password("Admin@12345"); admin.save()
        staff = []
        for i, (f, l) in enumerate([("Ravi", "Kumar"), ("Neha", "Singh"), ("Joby", "Thomas")], 1):
            u, _ = User.objects.get_or_create(username=f"staff{i}", defaults=dict(email=f"staff{i}@example.com", first_name=f, last_name=l,
                                              role="staff", employee_code=f"EMP00{i}", designation="Call Centre Executive"))
            u.set_password("Staff@12345"); u.save(); staff.append(u)
        if Lead.objects.exists():
            return self.stdout.write("Users ready. Sample data already present.")
        rnd = random.Random(7); now = timezone.now()
        banks = []
        for n in ["Demo National Bank", "Sample Finance Bank", "Example Credit Union"]:
            b = Bank.objects.create(name=n, contact_person="Relations Manager", phone="0484-0000000", email="loans@example.com")
            LoanScheme.objects.create(bank=b, name="Personal Loan Plus", loan_type="personal", interest_rate=Decimal("10.5"), min_amount=50000,
                                      max_amount=2500000, min_tenure_months=12, max_tenure_months=60, eligibility="Salaried, income above 20,000")
            LoanScheme.objects.create(bank=b, name="Home Loan Easy", loan_type="home", interest_rate=Decimal("8.7"), min_amount=500000,
                                      max_amount=10000000, min_tenure_months=60, max_tenure_months=300, eligibility="Age 21-60")
            banks.append(b)
        Lead.objects.bulk_create([Lead(name=f"{rnd.choice(FIRST)} {rnd.choice(LAST)}", phone=f"98{i:08d}", city=rnd.choice(CITY),
            email=f"lead{i}@example.com", loan_type=rnd.choice(["personal", "home", "business", "vehicle"]),
            loan_amount=rnd.choice([200000, 500000, 800000, 1500000]), source=rnd.choice(["Facebook", "Website", "Referral"]), created_by=admin)
            for i in range(1, 361)])
        pool = list(Lead.objects.order_by("pk").values_list("pk", flat=True))
        for k, u in enumerate(staff):
            assign(pool[k * 100:(k + 1) * 100], u, admin, "bulk", "Demo morning allocation")
        plan = {0: 62, 1: 100, 2: 35}
        for k, u in enumerate(staff):
            leads = list(Lead.objects.filter(assigned_to=u).order_by("pk"))
            calls = []
            for d in range(4):                                     # today + 3 previous days
                n = plan[k] if d == 0 else rnd.randint(70, 100)
                for lead in leads[:n]:
                    st = rnd.choices(["interested", "not_interested", "no_answer", "busy", "callback"], [18, 22, 30, 15, 15])[0]
                    calls.append(CallRecord(lead=lead, employee=u, status=st, duration_seconds=rnd.randint(10, 300), remarks="Demo call",
                                            called_at=now - timedelta(days=d, minutes=rnd.randint(1, 500) if d else rnd.randint(1, 300))))
            CallRecord.objects.bulk_create(calls)
            for lead in leads[:plan[k]]:
                last = lead.calls.order_by("-called_at").first()
                lead.status = {"interested": "interested", "not_interested": "not_interested"}.get(last.status, "contacted") if last else "assigned"
                lead.save(update_fields=["status"])
        for lead in Lead.objects.filter(status="interested"):
            c = Customer.objects.create(lead=lead, full_name=lead.name, phone=lead.phone, email=lead.email, city=lead.city,
                                        monthly_income=rnd.choice([25000, 40000, 65000]), required_amount=lead.loan_amount,
                                        loan_requirement=f"{lead.get_loan_type_display()} loan")
            if rnd.random() < .6:
                d = Document(customer=c, doc_type=rnd.choice(["aadhaar", "pan", "bank_statement", "salary_slip"]),
                             status=rnd.choice(["pending", "approved", "rejected"]), uploaded_by=lead.assigned_to)
                d.file.save("demo.pdf", ContentFile(b"%PDF-1.4 fictional demo document"), save=False); d.save()
            if rnd.random() < .5:
                FollowUp.objects.create(lead=lead, employee=lead.assigned_to, scheduled_at=now + timedelta(hours=rnd.randint(-30, 72)), notes="Collect documents")
            if rnd.random() < .45:
                sch = LoanScheme.objects.filter(loan_type=lead.loan_type if lead.loan_type in ("personal", "home") else "personal").order_by("?").first()
                amt = min(max(lead.loan_amount, sch.min_amount), sch.max_amount)
                app = LoanApplication.objects.create(customer=c, employee=lead.assigned_to, bank=sch.bank, scheme=sch, amount=amt,
                                                     tenure_months=sch.min_tenure_months, status="submitted")
                dec = LoanDecision.objects.create(application=app)
                r = rnd.random()
                if r < .4:
                    dec.decision, dec.approved_amount, dec.decided_on = "approved", amt, timezone.localdate(); app.status = "approved"
                    if r < .2:
                        dec.disbursed_amount, dec.disbursed_on = amt, timezone.localdate(); app.status = "disbursed"
                elif r < .6:
                    dec.decision, dec.rejection_reason, dec.decided_on = "rejected", "Low credit score (demo)", timezone.localdate(); app.status = "rejected"
                dec.save(); app.save()
        self.stdout.write(self.style.SUCCESS("Seeded. Admin: admin / Admin@12345 | Staff: staff1..3 / Staff@12345"))
