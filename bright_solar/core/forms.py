from django import forms
from django.contrib.auth.models import User
from .models import Appointment, ContactMessage, EmployeeProfile, Branch


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["customer_name", "phone", "email", "city", "location", "preferred_date", "preferred_time", "notes"]
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "preferred_time": forms.TimeInput(attrs={"type": "time"}),
            "location": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) < 10 or len(digits) > 13:
            raise forms.ValidationError("Enter a valid phone number (10–13 digits).")
        return phone


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "city", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}


class EmployeeCreateForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    temporary_password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    role = forms.ChoiceField(choices=EmployeeProfile.ROLE_CHOICES[1:])
    branch = forms.ModelChoiceField(queryset=Branch.objects.filter(is_active=True), required=False)
    phone = forms.CharField(max_length=20, required=False)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already in use.")
        return username
