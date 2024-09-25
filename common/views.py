from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .forms import *

# Create your views here.

def home(request):
    return render(request, 'home.html')

def customer_registration(request):
    if request.user.is_authenticated:
        return redirect('customer_dashboard') 
    else: 
        userform=CreateUserForm()
        customerform=CreateCustomerForm()
        if request.method=='POST':
            userform=CreateUserForm(request.POST)
            customerform=CreateCustomerForm(request.POST)
            if userform.is_valid() and customerform.is_valid():
                user=userform.save()
                customer=customerform.save(commit=False)
                customer.user=user 
                customer.save()
                return redirect('app_login')
        context={
            'userform':userform,
            'customerform':customerform,
        }
    return render(request, 'customer_registration.html', context)

def app_login(request):
    loginform=AppLoginForm()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # messages.success(request, "You are now logged in.")
            return redirect('home')  # Redirect to dashboard or homepage
        else:
            messages.error(request, "Invalid username or password.")
    context={
        'loginform': loginform
    }
    return render(request, 'login.html', context)

def app_logout(request):
    logout(request)
    return redirect('app_login')