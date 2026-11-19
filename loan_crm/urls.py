from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from customers.views import edit as customer_edit
from documents import views as docs
from followups.views import done as followup_done
from loan_applications.views import create as loan_create

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("dashboard.urls")),
    path("admin-portal/", include("dashboard.portal_urls")),                                  # desktop Admin
    path("m/", include(("dashboard.portal_urls", "mobile"), namespace="mobile")),            # Mobile Admin UI
    # shared action endpoints (permission-checked per record)
    path("actions/customers/<int:pk>/edit/", customer_edit, name="customer_edit"),
    path("actions/documents/upload/<int:cid>/", docs.upload, name="doc_upload"),
    path("actions/documents/<int:pk>/<str:decision>/", docs.verify, name="doc_verify"),
    path("secure/documents/<int:pk>/", docs.file, name="doc_file"),
    path("actions/loans/create/<int:cid>/", loan_create, name="loan_create"),
    path("actions/followups/<int:pk>/done/", followup_done, name="followup_done"),
]
