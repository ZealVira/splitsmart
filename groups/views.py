from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import Group, GroupMember
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth import get_user_model

User = get_user_model()

@login_required(login_url='login')
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        description = request.POST.get('description')
        created_by = request.user

        if not description:
            description = ""

        group = Group.objects.create(
            group_name=group_name,
            description=description,
            created_by=created_by
        )
        group.save()

        messages.success(request, "Group created successfully.")
        return redirect('index')

    return render(request, 'index.html') 



def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    members = GroupMember.objects.filter(group=group)
    return render(request, 'group_detail.html', {'group': group, 'members': members})


@login_required(login_url='login')
def add_member(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            print("User to be added:", user.email)
        
            if GroupMember.objects.filter(group=group, user=user).exists():
                messages.error(request, "User is already a member of this group.")
            else:
                GroupMember.objects.create(group=group, user=user)
                messages.success(request, f"{user.email} has been added to the group.")
        
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist.")

    return redirect('group_detail', pk=group_id)


def delete_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    if request.method == 'POST':
        group.delete()
        messages.success(request, "Group deleted successfully.")
        return redirect('index')

    return redirect('index')


def remove_member(request, group_id, user_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, pk=group_id)
        if group.created_by != request.user:
            return HttpResponseForbidden("Only group admins can remove members.")
        
        member = GroupMember.objects.filter(group=group, user__id=user_id).first()
        if member:
            member.delete()
            messages.success(request, "Member removed.")
        else:
            messages.warning(request, "User is not a member.")
        
    return redirect('index')


def leave_group(request, group_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, pk=group_id)
        member = GroupMember.objects.filter(group=group, user=request.user).first()
        
        if member:
            member.delete()
            messages.success(request, "You have left the group.")
        else:
            messages.warning(request, "You are not a member of this group.")
        
    return redirect('index')