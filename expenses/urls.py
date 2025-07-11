from django.urls import path
from . import views

urlpatterns = [
    path('add_expense/<int:pk>', views.add_expense, name='add_expense')
]