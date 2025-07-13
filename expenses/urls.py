from django.urls import path
from django.urls.resolvers import URLPattern

from . import views

app_name = "expenses"

urlpatterns: list[URLPattern] = [
    # path("", views.expense_list, name="list"),
    path("<int:pk>/add/", views.create_expense, name="create"),
    # path("<int:pk>/", views.expense_detail, name="detail"),
]
