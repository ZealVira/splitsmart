from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import Case, DecimalField, Sum, Value, When
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from sesame.utils import get_query_string, get_user

from .forms import GroupForm
from .models import Group, GroupMembership

User = get_user_model()


@login_required
def group_list(request: HttpRequest) -> HttpResponse:
    groups = Group.objects.filter(members=request.user)
    return render(request, "groups/list.html", {"groups": groups})


@login_required
def group_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            group.members.add(request.user)
            return redirect("groups:detail", pk=group.pk)

    return redirect("groups:list")


@login_required
def group_detail(request: HttpRequest, pk: int) -> HttpResponse:
    group = get_object_or_404(Group, pk=pk, members=request.user)

    # 1. last 10 expenses w/ payer
    expenses = group.expenses.select_related("paid_by")[:10]

    # 2. members ordered: admin first, then alphabetical
    members = group.members.order_by(
        Case(When(id=group.created_by_id, then=Value(0)), default=Value(1)), "full_name"
    )

    # 3. logged-in user balance inside this group
    owes_qs = group.expenses.filter(shares__user=request.user).aggregate(
        owes=Sum("shares__amount_owed", default=0, output_field=DecimalField())
    )
    paid_qs = group.expenses.filter(paid_by=request.user).aggregate(
        paid=Sum("amount", default=0, output_field=DecimalField())
    )

    balance = {
        "owes": owes_qs["owes"],
        "paid": paid_qs["paid"],
        "net": paid_qs["paid"] - owes_qs["owes"],
    }

    # 4. simple total group spend
    total_spend = group.expenses.aggregate(total=Sum("amount", default=0))["total"]     

    context = {
        "group": group,
        "members": members,
        "expenses": expenses,
        "is_admin": group.created_by == request.user,
        "balance": balance,
        "total_spend": total_spend,
    }
    return render(request, "groups/detail.html", context)


@login_required
@require_http_methods(["POST"])
def update_group_description(request, pk):
    group = get_object_or_404(Group, pk=pk, created_by=request.user)
    group.description = request.POST.get("description", "").strip()
    group.save()
    messages.success(request, "Description updated.")
    return redirect("groups:detail", pk=pk)


@login_required
@require_http_methods(["POST"])
def leave_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    group.members.remove(request.user)
    messages.info(request, "You left the group.")
    return redirect("groups:list")


@login_required
@require_http_methods(["POST"])
def delete_group(request, pk):
    group = get_object_or_404(Group, pk=pk, created_by=request.user)
    group.delete()
    messages.success(request, "Group deleted.")
    return redirect("groups:list")


@login_required
def invite_member(request: HttpRequest, pk: int) -> HttpResponse:
    group = get_object_or_404(Group, pk=pk, created_by=request.user)

    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"full_name": email.split("@")[0]},
            )
            path = reverse("groups:accept_invite", args=[group.pk])
            url = f"https://{get_current_site(request).domain}{path}{get_query_string(user)}"
            send_mail(
                subject=f"Join {group.name} on SplitSmart",
                message=f"Click here to accept the invite:\n\n{url}",
                from_email=None,
                recipient_list=[email],
            )
            return redirect("groups:detail", pk=group.pk)

    return render(request, "groups/add_member.html", {"group": group})


def accept_invite_join(request: HttpRequest, group_id: int) -> HttpResponse:
    """Sesame token lands here → auto-join group → redirect to detail."""
    user = get_user(request)
    if user is None:
        raise PermissionDenied

    group = get_object_or_404(Group, pk=group_id)
    GroupMembership.objects.get_or_create(group=group, user=user, defaults={"role": "member"})
    return redirect("groups:detail", pk=group.pk)
