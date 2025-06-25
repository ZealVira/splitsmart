from django.contrib import admin
from .models import User  # Import your custom User model

# Register your models here.
admin.site.register(User)  # Assuming 'User' is the model you want to register