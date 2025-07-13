from django.contrib import admin

from .models import Expense, ExpenseShare


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("description", "amount", "paid_by", "group", "created_at")
    list_filter = ("group", "paid_by", "created_at")
    search_fields = ("description", "group__name", "paid_by__username")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(ExpenseShare)
class ExpenseShareAdmin(admin.ModelAdmin):
    list_display = ("expense", "user", "amount_owed")
    list_filter = ("user",)
    search_fields = ("expense__description", "user__username")
