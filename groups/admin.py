from django.contrib import admin
from .models import Group, GroupMember  # Importing Group and GroupMember model

# Registering models here so that they are visible on admin panel.
admin.site.register(Group)
admin.site.register(GroupMember)  # Registering GroupMember model
