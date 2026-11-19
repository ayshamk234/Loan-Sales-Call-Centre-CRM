from django.urls import path
from . import views
urlpatterns = [path("approvals/", views.approvals, name="approvals_list"),
               path("approvals/<int:pk>/", views.decide, name="approvals_decide")]
