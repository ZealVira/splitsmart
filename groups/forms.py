from django import forms

from .models import Group


class GroupForm(forms.ModelForm):
    """Simple form to create or edit a group."""

    class Meta:
        model = Group
        fields = ("name", "description")

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Trip to Goa",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional short description…",
                }
            ),
        }
