from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import SignUpForm


# ---------- PUBLIC ----------
@require_http_methods(["GET"])
def home(request: HttpRequest) -> HttpResponse:
    """Landing page for non-authenticated visitors."""
    return render(request, "users/home.html")


@require_http_methods(["GET", "POST"])
def signup(request: HttpRequest) -> HttpResponse:
    """User registration."""
    initial = {}
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("expenses:list")
    else:
        # Pull ?email=… from invite link
        initial["email"] = request.GET.get("email", "")
        form = SignUpForm(initial=initial)

    return render(
        request,
        "users/signup.html",
        {
            "form": form,
            "prefilled_email": initial.get("email", ""),
        },
    )


# ---------- AUTHENTICATED ----------
@login_required
@require_http_methods(["GET"])
def profile(request: HttpRequest) -> HttpResponse:
    return render(request, "users/profile.html", {"user": request.user})


@require_http_methods(["POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("users:home")
