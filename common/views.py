from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .forms import CreateCustomerForm,CreateUserForm,AppLoginForm

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

def handle_redirect(user):
    if hasattr(user, 'customer'):
        return redirect('customer_dashboard')
    elif hasattr(user, 'staff'):
        return redirect('staff_dashboard')
    return redirect('home')

def app_login(request):
    if request.user.is_authenticated:
        user = request.user
        return handle_redirect(user)
    
    loginform=AppLoginForm()
    if request.method == 'POST':
        loginform = AppLoginForm(request.POST)
        if loginform.is_valid():
            username = loginform.cleaned_data['username']
            password = loginform.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return handle_redirect(user)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Form Errors!")

    context={
        'loginform': loginform
    }
    return render(request, 'login.html', context)

def app_logout(request):
    logout(request)
    return redirect('app_login')