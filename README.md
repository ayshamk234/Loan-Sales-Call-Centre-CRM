# Loan Sales & Call Centre CRM (Django + MySQL 8)

## Run locally
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # set DB_PASSWORD etc.
mysql -u root -p -e "CREATE DATABASE loan_crm CHARACTER SET utf8mb4;"
python manage.py makemigrations accounts employees leads lead_distribution customers \
  call_management followups targets documents banks loan_applications loan_approvals
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```
## Demo credentials (fictional)
| Role  | Username | Password |
|-------|----------|----------|
| Admin | admin    | Admin@12345 |
| Staff | staff1–staff3 | Staff@12345 |

## URLs
- `/accounts/login/` – login (role-based redirect)
- `/admin-portal/` – Admin · `/staff-portal/` – Staff · `/m/` – **Mobile Admin UI**

## Status
Phase 1 complete (structure, MySQL config, auth + roles, all models, dashboards).

## All phases implemented
Employees · Leads (+Pandas bulk upload, duplicate detection) · Distribution (auto / bulk / manual / reassign + history) ·
Customers · Calls (idempotent) · Follow-ups (pending / overdue / completed, bell reminder) · Daily targets · Documents
(validated upload, admin verification, permission-checked download) · Banks & schemes · Loan applications · Approvals,
disbursement & closure · Reports (CSV/Excel) · Staff portal (`/staff/`) · Mobile Admin (`/m/`, every admin page).

## Tests
`DB_ENGINE=sqlite python manage.py test` (12 scenarios: auth, access control, upload, assignment, call de-dup, targets,
documents, loan lifecycle, reports, every admin page on desktop + mobile).

## Deployment (e.g. PythonAnywhere / Render / VPS)
1. Set env vars from `.env.example` with `DEBUG=False`, a real `SECRET_KEY`, `ALLOWED_HOSTS=yourdomain`.
2. `pip install -r requirements.txt && python manage.py migrate && python manage.py seed_demo`
3. `python manage.py collectstatic --noinput` (WhiteNoise serves static files).
4. Run: `gunicorn loan_crm.wsgi`. Uploaded documents live in `media/` and are only served through `/secure/documents/<id>/`
   after a permission check – do NOT expose `media/` via the web server.
