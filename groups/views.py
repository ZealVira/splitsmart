from django.shortcuts import render
from .models import Group

def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        description = request.POST.get('description')
        created_by = request.user

        if not group_name:
            return render(request, 'index.html', {'error': 'Group name is required.'})

        group = Group.objects.create(
            group_name=group_name,
            description=description,
            created_by=created_by
        )
        group.save()

    return render(request, 'index.html') 