from django.contrib import admin

from .models import Group, GroupMembership


class MemberInline(admin.TabularInline):
    model = GroupMembership
    extra = 1
    readonly_fields = ("joined_at",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_by", "created_at", "member_count")
    list_filter = ("created_at",)
    search_fields = ("name", "created_by__email")
    readonly_fields = ("created_at",)
    inlines = (MemberInline,)

    def member_count(self, obj: Group) -> int:
        return obj.members.count()

    member_count.short_description = "Members"


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("group", "user", "role", "joined_at")
    list_filter = ("role", "joined_at")
    search_fields = ("group__name", "user__email")
    readonly_fields = ("joined_at",)
