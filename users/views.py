from django.shortcuts import render, redirect
from .models import User
from groups.models import Group, GroupMember
from django.db.models import Q
from django.contrib.auth import authenticate, login 
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def index(request):
    member = GroupMember.objects.filter(user=request.user).values_list('group_id', flat=True)
    groups = Group.objects.filter(Q(created_by=request.user) | Q(id__in=member)).order_by('-created_at')
    return render(request, 'index.html', {'groups': groups})

def signup_view(request):
    if request.method == 'POST':
        
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confpassword']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'signup.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully. Please log in.")
        print("User created successfully")
        return redirect('login')
    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid email or password.")
            print("Invalid credentials")

    return render(request, 'login.html')
# Create your views here.
