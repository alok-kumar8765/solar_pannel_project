from django.contrib import admin
from .models import Branch, EmployeeProfile, SolarProduct, Appointment, ContactMessage

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "area", "manager", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "area")

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "branch", "phone", "is_active_employee")
    list_filter = ("role", "branch", "is_active_employee")
    search_fields = ("user__username", "user__first_name", "user__last_name", "phone")

@admin.register(SolarProduct)
class SolarProductAdmin(admin.ModelAdmin):
    list_display = ("title", "system_type", "capacity_kw", "price_from", "is_featured", "is_active")
    list_filter = ("system_type", "is_featured", "is_active")
    search_fields = ("title", "description")

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "phone", "product", "branch", "assigned_to", "status", "preferred_date")
    list_filter = ("status", "branch", "product__system_type")
    search_fields = ("customer_name", "phone", "city")

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "city", "is_resolved", "created_at")
    list_filter = ("is_resolved",)
    search_fields = ("name", "phone", "message")
