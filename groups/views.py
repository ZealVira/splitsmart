from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Group, GroupMember
from expenses.models import Expense  # Import from other app
from django.db.models import Sum


User = get_user_model()

@login_required(login_url='login')
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        description = request.POST.get('description', '').strip()
        created_by = request.user

        group = Group.objects.create(
            group_name=group_name,
            description=description,
            created_by=created_by
        )
        messages.success(request, "Group created successfully.")
        return redirect('group_detail', pk=group.pk)

    return render(request, 'index.html')

@login_required(login_url='login')
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    expenses = Expense.objects.filter(group=group).order_by('-created_at')

    members_qs = GroupMember.objects.filter(group=group).select_related('user')

    # Actual members (excluding admin)
    members = members_qs

    # All members (including admin)
    all_member_ids = list(members_qs.values_list('user', flat=True))
    if group.created_by.id not in all_member_ids:
        all_member_ids.append(group.created_by.id)
        # print(all_member_ids)
    
    all_members = User.objects.filter(id__in=all_member_ids)
    
    member_own = Expense.objects.filter(group=group).aggregate(total=Sum('amount'))['total'] or 0


    is_admin = request.user == group.created_by

    return render(request, 'group_detail.html', {
        'group': group,
        'members': members,
        'all_members': all_members,
        'is_admin': is_admin,
        'expenses': expenses,
        'group_total' : member_own
    })








@login_required(login_url='login')
def add_member(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    
    if request.user != group.created_by:
        return HttpResponseForbidden("Only group admins can add members.")
    
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        
        try:
            user = User.objects.get(email=email)
            if GroupMember.objects.filter(group=group, user=user).exists():
                messages.warning(request, "User is already a member.")
            else:
                GroupMember.objects.create(group=group, user=user)
                messages.success(request, f"{user.email} added to group.")
        except User.DoesNotExist:
            signup_link = f"{request.scheme}://{request.get_host()}/signup/?email={email}&group_id={group.id}"
            messages.warning(request, f"No user found with email {email}. Share this signup link: {signup_link}")

            # messages.error(request, "User not found.")
            
    return redirect('group_detail', pk=group_id)

@require_POST
@login_required(login_url='login')
def delete_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    
    if group.created_by != request.user:
        return HttpResponseForbidden("Only group creator can delete the group.")
        
    group.delete()
    messages.success(request, "Group deleted successfully.")
    return redirect('index')

@require_POST
@login_required(login_url='login')
def remove_member(request, group_id, user_id):
    group = get_object_or_404(Group, pk=group_id)
    
    if group.created_by != request.user:
        return HttpResponseForbidden("Only group admins can remove members.")
        
    member = get_object_or_404(GroupMember, group=group, user__id=user_id)
    member.delete()
    messages.success(request, "Member removed.")
    return redirect('group_detail', pk=group_id)

@require_POST
@login_required(login_url='login')
def leave_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    
    if group.created_by == request.user:
        messages.error(request, "Admins cannot leave their own group. Delete or transfer admin first.")
        return redirect('group_detail', pk=group_id)
        
    member = GroupMember.objects.filter(group=group, user=request.user).first()
    if member:
        member.delete()
        messages.success(request, "You have left the group.")
    else:
        messages.warning(request, "You are not a member of this group.")
        
    return redirect('index')

@require_POST
@login_required(login_url='login')
def update_group_description(request, pk):
    group = get_object_or_404(Group, pk=pk)
    
    if group.created_by != request.user:
        return HttpResponseForbidden("Only group admins can edit the description.")
        
    description = request.POST.get('description', '').strip()
    group.description = description
    group.save()
    messages.success(request, "Description updated.")
    return redirect('group_detail', pk=pk)