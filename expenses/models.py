from django.db import models
from django.contrib.auth import get_user_model
from groups.models import Group

User = get_user_model()

class Expense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses_paid')
    amount = models.DecimalField(max_digits=8, decimal_places=2)  # supports up to 999,999.99
    description = models.TextField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.paid_by.username} paid ₹{self.amount} in {self.group.group_name}"


class Payment(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_settled = models.BooleanField(default=False)
    note = models.TextField(blank=True, max_length=50)
    
    def __str__(self):
        return f"{self.from_user.username} paid {self.to_user.username} ₹{self.amount}"

