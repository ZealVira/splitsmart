from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from groups.models import Group, GroupMember
from .models import Expense, Payment


User = get_user_model()

@login_required(login_url='login')
def add_expense(request, pk):
    group = get_object_or_404(Group, pk=pk)

    if request.method == 'POST':
        description = request.POST['description']
        amount = request.POST['amount']
        paid_by_id = request.POST['paid_by']
        # print(paid_by_id)
        paid_by = User.objects.get(id = paid_by_id)
        
        shared_with = request.POST.getlist('shared_with[]')

        if not shared_with:
            messages.error(request, "Please select at least one member to share the expense with.")
            return redirect('group_detail', pk=pk)
        
        expense = Expense.objects.create(group=group, paid_by=paid_by, amount=amount, description=description)
        expense.save()
        messages.success(request, "expense created successfully")
    
    return redirect('group_detail', pk=pk)

