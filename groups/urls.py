from django.urls import path, include
from . import views

urlpatterns = [
    path('create_group', views.create_group, name='create_group'),
]