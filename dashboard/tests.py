import io
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from banks.models import Bank, LoanScheme
from call_management.models import CallRecord
from customers.models import Customer
from documents.models import Document
from followups.models import FollowUp
from lead_distribution.models import LeadAssignment
from leads.models import Lead
from loan_applications.models import LoanApplication

class CRMTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin", password="x", role="admin")
        self.s1 = User.objects.create_user("s1", password="x", role="staff", first_name="A")
        self.s2 = User.objects.create_user("s2", password="x", role="staff", first_name="B")
        self.lead = Lead.objects.create(name="Test", phone="9876543210", assigned_to=self.s1, status="assigned")

    def login(self, u): self.client.force_login(u)

    def test_login_and_redirects(self):
        r = self.client.post(reverse("accounts:login"), {"username": "admin", "password": "x"})
        self.assertEqual(r.status_code, 302)
        self.login(self.admin); self.assertRedirects(self.client.get("/"), reverse("dashboard"))
        self.login(self.s1); self.assertRedirects(self.client.get("/"), reverse("staff_dashboard"))

    def test_unauthorized_access(self):
        self.assertEqual(self.client.get("/admin-portal/").status_code, 302)
        self.login(self.s1)
        for u in ["/admin-portal/", "/admin-portal/leads/", "/m/", "/m/reports/", "/admin-portal/employees/"]:
            self.assertEqual(self.client.get(u).status_code, 403, u)
        self.login(self.admin); self.assertEqual(self.client.get("/staff/").status_code, 403)

    def test_staff_cannot_open_other_leads(self):
        self.login(self.s2); self.assertEqual(self.client.get(reverse("staff_lead", args=[self.lead.pk])).status_code, 404)

    def test_employee_creation(self):
        self.login(self.admin)
        r = self.client.post(reverse("employees_new"), dict(username="new1", first_name="N", last_name="E", password="Str0ng!Pass99", daily_target=100, is_active="on"))
        self.assertEqual(r.status_code, 302); self.assertEqual(User.objects.get(username="new1").role, "staff")

    def test_bulk_upload_and_duplicates(self):
        self.login(self.admin)
        csv = b"name,phone\nAnil,9000000001\nBindu,9000000002\nDup,9000000001\nBad,123\nExisting,9876543210\n"
        self.client.post(reverse("leads_upload"), {"file": SimpleUploadedFile("l.csv", csv)})
        self.assertEqual(Lead.objects.count(), 3)          # 1 existing + 2 new

    def test_assignment_modes_and_history(self):
        self.login(self.admin)
        Lead.objects.bulk_create([Lead(name=f"L{i}", phone=f"90000001{i:02d}") for i in range(10)])
        self.client.post(reverse("distribute"), {"action": "auto", "employees": [self.s1.pk, self.s2.pk], "cap": 4})
        self.assertEqual(Lead.objects.filter(assigned_to=self.s2).count(), 4)
        self.client.post(reverse("distribute"), {"action": "reassign", "from_emp": self.s2.pk, "to_emp": self.s1.pk})
        self.assertEqual(Lead.objects.filter(assigned_to=self.s2).count(), 0)
        for l in Lead.objects.all():
            self.assertLessEqual(LeadAssignment.objects.filter(lead=l, is_active=True).count(), 1)

    def test_call_idempotent_target_and_followup(self):
        self.login(self.s1); url = reverse("staff_lead", args=[self.lead.pk])
        data = dict(status="interested", duration_seconds=60, remarks="ok", submit_token="11111111-1111-1111-1111-111111111111",
                    followup_at=(timezone.now() + timezone.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"))
        self.client.post(url, data); self.client.post(url, data)           # double submit
        self.assertEqual(CallRecord.objects.count(), 1)
        self.assertEqual(FollowUp.objects.count(), 1); self.assertTrue(Customer.objects.filter(lead=self.lead).exists())
        self.lead.refresh_from_db(); self.assertEqual(self.lead.status, "interested")
        from targets.services import progress
        p = progress(self.s1); self.assertEqual((p["completed"], p["remaining"], p["percent"]), (1, 99, 1))
        bad = dict(data, submit_token="22222222-2222-2222-2222-222222222222", followup_at="2001-01-01T10:00")
        self.client.post(url, bad); self.assertEqual(CallRecord.objects.count(), 1)

    def _customer(self):
        return Customer.objects.create(lead=self.lead, full_name="Test", phone=self.lead.phone)

    def test_document_upload_validation_and_verification(self):
        c = self._customer(); self.login(self.s1)
        up = reverse("doc_upload", args=[c.pk])
        self.client.post(up, {"doc_type": "pan", "file": SimpleUploadedFile("x.exe", b"MZ")})
        self.client.post(up, {"doc_type": "pan", "file": SimpleUploadedFile("x.pdf", b"not a pdf")})
        self.assertEqual(Document.objects.count(), 0)
        self.client.post(up, {"doc_type": "pan", "file": SimpleUploadedFile("x.pdf", b"%PDF-1.4 demo")})
        d = Document.objects.get(); self.assertEqual(d.status, "pending")
        self.client.post(reverse("doc_verify", args=[d.pk, "approved"])); d.refresh_from_db(); self.assertEqual(d.status, "pending")  # staff blocked
        self.login(self.s2); self.assertEqual(self.client.get(reverse("doc_file", args=[d.pk])).status_code, 403)
        self.login(self.admin); self.client.post(reverse("doc_verify", args=[d.pk, "approved"]))
        d.refresh_from_db(); self.assertEqual((d.status, d.verified_by), ("approved", self.admin))

    def test_loan_lifecycle(self):
        c = self._customer(); b = Bank.objects.create(name="B")
        sch = LoanScheme.objects.create(bank=b, name="S", interest_rate=9, min_amount=1000, max_amount=100000)
        self.login(self.s1)
        self.client.post(reverse("loan_create", args=[c.pk]), dict(bank=b.pk, scheme=sch.pk, amount=999999, tenure_months=12))
        self.assertEqual(LoanApplication.objects.count(), 0)              # out of scheme range
        self.client.post(reverse("loan_create", args=[c.pk]), dict(bank=b.pk, scheme=sch.pk, amount=50000, tenure_months=12))
        a = LoanApplication.objects.get(); self.assertTrue(a.reference_no.startswith("LN"))
        self.login(self.admin); url = reverse("approvals_decide", args=[a.pk])
        self.client.post(url, dict(decision="rejected")); a.refresh_from_db(); self.assertEqual(a.status, "submitted")  # reason required
        self.client.post(url, dict(decision="approved", approved_amount=50000)); a.refresh_from_db(); self.assertEqual(a.status, "approved")
        self.client.post(url, dict(decision="approved", approved_amount=50000, disbursed_on="2026-11-19", disbursed_amount=50000))
        self.client.post(url, dict(decision="approved", approved_amount=50000, disbursed_on="2026-11-19", closed_on="2026-11-20"))
        a.refresh_from_db(); self.assertEqual(a.status, "closed")

    def test_reports_export_and_all_mobile_pages(self):
        self.login(self.admin)
        r = self.client.get(reverse("reports"), {"report": "employee_perf", "export": "csv"}); self.assertEqual(r.status_code, 200)
        r = self.client.get(reverse("reports"), {"report": "daily_calls", "export": "xlsx"}); self.assertEqual(r.status_code, 200)
        from dashboard.context import ADMIN_NAV
        for _, name, _ in ADMIN_NAV:
            for ns in ("", "mobile:"):
                self.assertEqual(self.client.get(reverse(ns + name)).status_code, 200, ns + name)
