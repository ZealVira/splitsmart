from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from groups.models import Group

from .forms import ExpenseForm
from .models import Expense, ExpenseShare


@login_required
@require_http_methods(["GET", "POST"])
def create_expense(request, pk):
    """Full page for adding an expense."""
    group = get_object_or_404(Group, pk=pk, members=request.user)

    if request.method == "POST":
        form = ExpenseForm(group, request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # create expense header
            expense = Expense.objects.create(
                group=group,
                description=cd["description"],
                amount=cd["amount"],
                paid_by=cd["paid_by"],
            )

            shared_users = cd["shared_with"]
            total = cd["amount"]
            count = shared_users.count()

            custom_amounts = request.POST.getlist("amounts")

            if len(custom_amounts) == count:
                valid = True
                amounts = []
                for val in custom_amounts:
                    try:
                        amount = Decimal(val.strip())
                        amounts.append(amount)
                    except (InvalidOperation, ValueError):
                        valid = False
                        break

                if valid:
                    for user, amount in zip(shared_users, amounts):
                        ExpenseShare.objects.create(expense=expense, user=user, amount_owed=amount)
                else:
                    expense.delete()  # clean up orphaned expense
                    messages.error(
                        request, "Invalid amount(s) entered. Please enter valid numbers."
                    )
                    return render(
                        request, "expenses/create_expense.html", {"form": form, "group": group}
                    )
            else:
                # fallback to equal split
                split = total / count
                for user in shared_users:
                    ExpenseShare.objects.create(expense=expense, user=user, amount_owed=split)

            messages.success(request, "Expense added.")
            return redirect("groups:detail", pk=pk)
    else:
        form = ExpenseForm(group)

    return render(request, "expenses/create_expense.html", {"form": form, "group": group})
