from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class CRMUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("CRM", {"fields": ("role", "phone", "employee_code", "designation", "daily_target", "joined_on")}),)
    list_display = ("username", "get_full_name", "role", "is_active")
