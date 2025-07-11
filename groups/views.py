from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Group, GroupMember

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

def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    members = GroupMember.objects.filter(group=group).select_related('user')
    is_admin = request.user == group.created_by
    return render(request, 'group_detail.html', {
        'group': group,
        'members': members,
        'is_admin': is_admin
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
            messages.error(request, "User not found.")
            
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