from django.urls import path

from . import views

app_name = "groups"

urlpatterns = [
    path("", views.group_list, name="list"),
    path("create/", views.group_create, name="create"),
    path("<int:pk>/", views.group_detail, name="detail"),
    path("<int:pk>/add-member/", views.invite_member, name="add_member"),
    path("invite/<int:group_id>/accept/", views.accept_invite_join, name="accept_invite"),
    path("<int:pk>/leave/", views.leave_group, name="leave_group"),
    path("<int:pk>/delete/", views.delete_group, name="delete"),
    path("<int:pk>/update/", views.update_group_description, name="update_description"),
]
