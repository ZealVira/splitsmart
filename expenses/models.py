from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Expense(models.Model):
    """
    A single expense in a group.
    """

    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    paid_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expenses_paid",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.description} – {self.amount} in {self.group.name}"


class ExpenseShare(models.Model):
    """
    How much each member owes for a given expense.
    """

    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name="shares",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expense_shares",
    )
    amount_owed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        unique_together = ("expense", "user")

    def __str__(self):
        return f"{self.user} owes {self.amount_owed} for {self.expense}"
