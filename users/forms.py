from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ("full_name", "email", "password1", "password2")