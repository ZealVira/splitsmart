from django.urls import path
from . import views

urlpatterns = [
    path('add_expense/<int:pk>', views.add_expense, name='add_expense'),
    path('view_all_expenses/<int:pk>', views.view_all_expenses, name='view_all_expenses'),
    path('view_for_month/<int:pk>', views.view_for_month, name='view_for_month'),
    path('view_pending_expenses/<int:pk>', views.view_pending_expenses, name='view_pending_expenses'),
    path('update_expense_status', views.update_expense_status, name='update_expense_status')
]