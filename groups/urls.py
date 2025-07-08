from django.urls import path, include
from . import views

urlpatterns = [
    path('create_group', views.create_group, name='create_group'),
    path('<int:pk>/', views.group_detail, name='group_detail'),
    path('<int:group_id>/add_member/', views.add_member, name='add_member'),
    path('<int:group_id>/delete_group/', views.delete_group, name='delete_group'),
    path('<int:group_id>/remove_member/<int:user_id>/', views.remove_member, name='remove_member'),
    path('<int:group_id>/leave_group/', views.leave_group, name='leave_group'),

]