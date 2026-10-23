from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import AppointmentForm, ContactForm, EmployeeCreateForm
from .models import Appointment, Branch, EmployeeProfile, SolarProduct


def home(request):
    featured = SolarProduct.objects.filter(is_active=True, is_featured=True)[:3]
    if not featured:
        featured = SolarProduct.objects.filter(is_active=True)[:3]
    return render(request, "core/home.html", {"featured": featured})


def products(request):
    items = SolarProduct.objects.filter(is_active=True)
    system_type = request.GET.get("type", "")
    if system_type in {"on_grid", "off_grid", "hybrid"}:
        items = items.filter(system_type=system_type)
    return render(request, "core/products.html", {"products": items, "selected_type": system_type})


def product_detail(request, pk):
    product = get_object_or_404(SolarProduct, pk=pk, is_active=True)
    return render(request, "core/product_detail.html", {"product": product})


def appointment_create(request, product_id):
    product = get_object_or_404(SolarProduct, pk=product_id, is_active=True)
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.product = product
            appointment.save()
            messages.success(request, "Your consultation request has been received. Our team will contact you.")
            return redirect("home")
    else:
        form = AppointmentForm()
    return render(request, "core/appointment_form.html", {"form": form, "product": product})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you. Your message has been submitted.")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        error = "Invalid username or password."
    return render(request, "core/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("home")


def get_profile(user):
    return getattr(user, "employee_profile", None)


@login_required
def dashboard(request):
    profile = get_profile(request.user)
    is_owner = request.user.is_superuser or (profile and profile.role == "owner")
    is_manager = profile and profile.role == "manager"
    if not (is_owner or is_manager or (profile and profile.role in {"sales", "accounts", "field"})):
        return HttpResponseForbidden("Your account does not have staff dashboard access.")

    if is_owner:
        qs = Appointment.objects.select_related("product", "branch", "assigned_to")
        employees = EmployeeProfile.objects.select_related("user", "branch").filter(is_active_employee=True)
        branches = Branch.objects.filter(is_active=True)
    elif is_manager:
        qs = Appointment.objects.filter(branch=profile.branch).select_related("product", "branch", "assigned_to")
        employees = EmployeeProfile.objects.select_related("user", "branch").filter(branch=profile.branch, is_active_employee=True)
        branches = Branch.objects.filter(pk=profile.branch_id) if profile.branch_id else Branch.objects.none()
    else:
        qs = Appointment.objects.filter(assigned_to=request.user).select_related("product", "branch", "assigned_to")
        employees = EmployeeProfile.objects.filter(user=request.user)
        branches = Branch.objects.filter(pk=profile.branch_id) if profile and profile.branch_id else Branch.objects.none()

    status_counts = {row["status"]: row["total"] for row in qs.values("status").annotate(total=Count("id"))}
    return render(request, "core/dashboard.html", {
        "appointments": qs[:100], "employees": employees, "branches": branches,
        "status_counts": status_counts, "is_owner": bool(is_owner),
        "is_manager": bool(is_manager), "profile": profile,
    })


def can_manage_appointment(user, appointment):
    profile = get_profile(user)
    if user.is_superuser or (profile and profile.role == "owner"):
        return True
    return bool(profile and profile.role == "manager" and profile.branch_id == appointment.branch_id)


@login_required
def assign_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if not can_manage_appointment(request.user, appointment):
        return HttpResponseForbidden("You cannot assign this enquiry.")
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        employee = get_object_or_404(EmployeeProfile, pk=employee_id, is_active_employee=True, role="field")
        if not (request.user.is_superuser or (get_profile(request.user) and get_profile(request.user).role == "owner")):
            if employee.branch_id != get_profile(request.user).branch_id:
                return HttpResponseForbidden("Choose a field employee from your branch.")
        appointment.assigned_to = employee.user
        appointment.branch = employee.branch
        appointment.status = "assigned"
        appointment.save()
        messages.success(request, "Enquiry assigned successfully.")
    return redirect("dashboard")


@login_required
def update_appointment_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    profile = get_profile(request.user)
    allowed = request.user.is_superuser or (profile and profile.role == "owner") or appointment.assigned_to_id == request.user.id
    if not allowed:
        return HttpResponseForbidden("You cannot update this enquiry.")
    if request.method == "POST":
        status = request.POST.get("status")
        allowed_statuses = {value for value, _ in Appointment.STATUS_CHOICES}
        if status in allowed_statuses:
            appointment.status = status
            appointment.cancellation_reason = request.POST.get("cancellation_reason", "").strip() if status == "cancelled" else ""
            appointment.save()
            messages.success(request, "Enquiry status updated.")
    return redirect("dashboard")


@login_required
def employee_create(request):
    profile = get_profile(request.user)
    if not (request.user.is_superuser or (profile and profile.role == "owner")):
        return HttpResponseForbidden("Only the owner can create employee accounts in this starter.")
    if request.method == "POST":
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data["username"], password=data["temporary_password"],
                first_name=data["first_name"], last_name=data["last_name"], email=data["email"]
            )
            EmployeeProfile.objects.create(user=user, role=data["role"], branch=data["branch"], phone=data["phone"])
            messages.success(request, f"Employee account created for {user.username}.")
            return redirect("dashboard")
    else:
        form = EmployeeCreateForm()
    return render(request, "core/employee_form.html", {"form": form})
