from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OwnerProfile


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Role Info", {"fields": ("role", "phone", "is_owner_approved")}),
    )
    list_display = ("username", "email", "role", "is_owner_approved", "is_staff")
    list_filter = ("role", "is_owner_approved")


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OwnerProfile)