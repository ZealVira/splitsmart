from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(max_length=100)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

    def __str__(self):
        return self.email
