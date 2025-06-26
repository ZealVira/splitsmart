from django.shortcuts import render, redirect, get_object_or_404
from .models import Group, GroupMember
from django.contrib.auth.decorators import login_required

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
        return redirect('index')

    return render(request, 'index.html') 



def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    members = GroupMember.objects.filter(group=group)
    return render(request, 'group_detail.html', {'group': group, 'members': members})