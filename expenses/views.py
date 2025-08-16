import json
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from groups.models import Group, GroupMember
from .models import Expense, Payment
import calendar

User = get_user_model()

@login_required(login_url='login')
def add_expense(request, pk):
    group = get_object_or_404(Group, pk=pk)

    if request.method == 'POST':
        description = request.POST['description']
        amount = request.POST['amount']
        paid_by_id = request.POST['paid_by']
        split_type = request.POST.get('split_type')
        print(split_type)
        paid_by = User.objects.get(id = paid_by_id)
        
        shares = {}

        if(split_type == 'equal'):
            group = get_object_or_404(Group, pk=pk)
            members = GroupMember.objects.filter(group=group).select_related('user')

            split_amount = round(int(amount) / len(members), 2)
            for member in members:
                shares[member.user.id] = split_amount

        else:
            shared_with = request.POST.getlist('shared_with')
            print(shared_with)

            if not shared_with:
                messages.error(request, "Please select at least one member to share the expense with.")
                return redirect('group_detail', pk=pk)
            
            
            # if split_type == 'equal':
            #     split_amount = round(int(amount) / len(shared_with), 2)
            #     for uid in shared_with:
            #         shares[uid] = split_amount
            # else:
            for uid in shared_with:
                amt = request.POST.get(f'amounts_{uid}', '0').strip()
                shares[uid] = float(amt or 0)


        expense = Expense.objects.create(group=group, paid_by=paid_by, amount=amount, description=description)
        expense.save()
        to_user = request.user

        for user_id, share_amount in shares.items():
            user = User.objects.get(pk=user_id)
            Payment.objects.create(
                from_user = user,
                to_user = to_user,
                group = group,
                amount = share_amount,
                note = description
            )

        messages.success(request, "expense created successfully")
    
    return redirect('group_detail', pk=pk)


def view_all_expenses(request, pk):
    group = get_object_or_404(Group, pk=pk)
    expenses = Expense.objects.filter(group=group).order_by('-created_at')
    month_choices = [(i, calendar.month_name[i]) for i in range(1, 13)]

    return render(request, 'groups/view_expenses.html', {'group': group, 'expenses': expenses, 'month_choices': month_choices})


def view_for_month(request, pk):
    group = get_object_or_404(Group, pk=pk)
    month_choices = [(i, calendar.month_name[i]) for i in range(1, 13)]

    # print(month_choices)
    month = int(request.GET.get('month', 1))  # Default to January if no month is provided

    if month < 1 or month > 12:
        return HttpResponseForbidden("Invalid month")
    expenses = Expense.objects.filter(group=group, created_at__month=month).order_by('-created_at')
    return render(request, 'groups/view_expenses.html', {'group': group, 'expenses': expenses, 'month_choices': month_choices})


def view_pending_expenses(request, pk):
    group = get_object_or_404(Group, pk=pk)
    pending_expenses = Payment.objects.filter(to_user=request.user, group=group, is_settled=False).order_by('-created_at')
    print(pending_expenses)
    return render(request, 'group_detail.html', {'group': group, 'pending_expenses': pending_expenses})


@login_required
def update_expense_status(request):
    if request.method == "POST":
        data = json.loads(request.body)
        payment_id = data.get("expense_id")
        checked = data.get("checked")

        try:
            expense = Payment.objects.get(id=payment_id)
            expense.is_settled = checked  # assuming you added this boolean field
            expense.save()
            
            print(payment_id)
            print(checked)

            messages.success(request, "Expense status updated successfully.")
            return JsonResponse({
                "status": "success",
                "expense_id": payment_id,
                "checked": checked
            })
        except Payment.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Expense not found"}, status=404)
