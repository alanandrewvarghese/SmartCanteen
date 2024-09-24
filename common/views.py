from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
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
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('app_login')