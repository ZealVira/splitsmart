from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """
    A single expense-sharing group (trip, house, etc.).
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, related_name="owned_groups", on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="groups_joined", through="GroupMembership")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "created_by"], name="unique_group_name_per_creator"
            )
        ]

    def __str__(self) -> str:
        return self.name


class GroupMembership(models.Model):
    """
    Through table so we can store extra data (role, joined date, etc.).
    """

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(
        max_length=10,
        choices=[("admin", "Admin"), ("member", "Member")],
        default="member",
    )

    class Meta:
        unique_together = ("group", "user")  # one membership per user per group

    def __str__(self):
        return f"{self.user.email} in {self.group.name} ({self.role})"
