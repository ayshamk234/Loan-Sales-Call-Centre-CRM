from django.urls import path
from . import views
urlpatterns = [path("followups/", views.followups_list, name="followups_list")]
