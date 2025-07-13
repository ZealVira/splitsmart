from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class ExpenseForm(forms.Form):
    description = forms.CharField(
        label="Title / Note",
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "e.g. Dinner at Pizza Hut"}
        ),
    )
    amount = forms.DecimalField(
        label="Amount",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": "0.01", "placeholder": "₹"}
        ),
    )
    paid_by = forms.ModelChoiceField(
        label="Paid by",
        queryset=User.objects.none(),  # set in __init__
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    shared_with = forms.ModelMultipleChoiceField(
        label="Share with",
        queryset=User.objects.none(),  # set in __init__
        widget=forms.CheckboxSelectMultiple,
    )
    # optional custom split amounts
    custom_amounts = forms.JSONField(required=False, widget=forms.HiddenInput)

    def __init__(self, group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        members_qs = group.members.all()
        if isinstance(self.fields["paid_by"], forms.ModelChoiceField):
            self.fields["paid_by"].queryset = members_qs
        if isinstance(self.fields["shared_with"], forms.ModelMultipleChoiceField):
            self.fields["shared_with"].queryset = members_qs
