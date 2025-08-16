from django.shortcuts import render, redirect
from .models import User
from groups.models import Group, GroupMember
from expenses.models import Payment
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum


@login_required(login_url='login')
def index(request):
    user = request.user
    
    # list the groups created by the user
    group_admin = Group.objects.filter(created_by=user).values_list('id', flat=True)
    
    member = GroupMember.objects.filter(user=request.user).values_list('group_id', flat=True)
    groups = Group.objects.filter(Q(created_by=request.user) | Q(id__in=member)).order_by('-created_at')
    
    # Total amount user SHOULD RECEIVE (others owe user)
    you_are_owed = Payment.objects.filter(
        to_user=request.user,
        is_settled=False
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Total amount user OWES (user owes to others)
    you_owe = Payment.objects.filter(
        from_user=request.user,
        is_settled=False
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Net balance
    net_balance = you_are_owed - you_owe
    
    return render(request, 'index.html', {
        'groups': groups, 
        'group_admin': group_admin,
        'total_owed': you_are_owed,
        'total_owes': you_owe,
        'net_balance': net_balance
    })


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confpassword']
        group_id = request.POST.get('group_id')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html', {'prefilled_email': email})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'signup.html', {'prefilled_email': email})

        user = User.objects.create_user(username=username, email=email, password=password)

        if group_id:
            try:
                group = Group.objects.get(id=int(group_id))
                GroupMember.objects.create(group=group, user=user)
                print(f'{email} added to grp')
                messages.success(request, f'Added to group "{group.group_name}" successfully!')
            except Group.DoesNotExist:

                messages.warning(request, "Group not found. Created account, but couldn't join group.")

        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')
    else:
        getEmail = request.GET.get('email', '')
    #     #group_id = request.GET.get('group_id', '')

    
        return render(request, 'signup.html', {'prefilled_email': getEmail})


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

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

def landing_view(request):
    return render(request, 'landing.html')

@login_required(login_url='login')
def profile_view(request):
    you_are_owed = Payment.objects.filter(
        to_user=request.user,
        is_settled=False
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Total amount user OWES (user owes to others)
    you_owe = Payment.objects.filter(
        from_user=request.user,
        is_settled=False
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Net balance
    net_balance = you_are_owed - you_owe
    return render(request, 'profile.html', {
        'you_are_owed': you_are_owed,
        'you_owe': you_owe,
        'net_balance': net_balance
    })