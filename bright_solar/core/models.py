from django.conf import settings
from django.db import models
from django.utils import timezone


class Branch(models.Model):
    name = models.CharField(max_length=120)
    area = models.CharField(max_length=160)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="managed_branches")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} — {self.area}"


class EmployeeProfile(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner / S.K."),
        ("manager", "Branch Manager"),
        ("sales", "Sales"),
        ("accounts", "Accounts"),
        ("field", "Field Employee"),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="employee_profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="field")
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL,
                               related_name="employees")
    phone = models.CharField(max_length=20, blank=True)
    is_active_employee = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"


class SolarProduct(models.Model):
    SYSTEM_CHOICES = [("on_grid", "On-Grid"), ("off_grid", "Off-Grid"), ("hybrid", "Hybrid")]
    title = models.CharField(max_length=180)
    system_type = models.CharField(max_length=20, choices=SYSTEM_CHOICES)
    capacity_kw = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price_from = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    benefits = models.TextField(blank=True, help_text="One benefit per line")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "title"]

    def __str__(self):
        return self.title


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("visit_scheduled", "Visit Scheduled"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
    ]
    customer_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    city = models.CharField(max_length=120)
    location = models.TextField()
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    product = models.ForeignKey(SolarProduct, on_delete=models.PROTECT, related_name="appointments")
    notes = models.TextField(blank=True)
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL,
                               related_name="appointments")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="assigned_appointments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer_name} — {self.product.title} ({self.get_status_display()})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=120, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} — {self.phone}"
