from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .forms import CreateCustomerForm,CreateUserForm,AppLoginForm,PasswordResetRequestForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import login
from django.core.mail import EmailMultiAlternatives

# Create your views here.
User = get_user_model()

def password_reset_request(request):
    print("Request method:", request.method) 
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        print("Form is valid:", form.is_valid())
        if form.is_valid():
            email = form.cleaned_data["email"]
            print("Email entered:", email)  
            associated_users = User.objects.filter(email=email)
            print("Number of associated users found:", associated_users.count())  
            if associated_users.exists():
                for user in associated_users:
                    print(f"Processing user: {user.username}")

                    token = default_token_generator.make_token(user)
                    print("Generated token:", token)  
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    print("Encoded UID:", uid)  
                    password_reset_url = request.build_absolute_uri(
                        f"/reset/{uid}/{token}/"
                    )
                    print("Password reset URL:", password_reset_url)  

                    email_subject = "Password Reset Requested"
                    email_body = render_to_string("password_reset_email.html", {
                        "password_reset_url": password_reset_url,
                        "user": user,
                    })
                    text_content = "You requested a password reset. Visit the following link: {}".format(password_reset_url)

                    email_message = EmailMultiAlternatives(
                        email_subject, text_content, "smartcanteen@gmail.com", [email]
                    )
                    email_message.attach_alternative(email_body, "text/html")
                    email_message.send()
                    print(f"HTML Password reset email sent to {email}")

                    # print("Email body rendered")  # Debugging line to confirm email body rendering
                    # send_mail(email_subject, email_body, "smartcanteen@gmail.com", [email], fail_silently=False,)
                    # print(f"Password reset email sent to {email}")  # Debugging line to confirm email sending
                return redirect('app_login')
            else:
                print(f"No users found with email {email}")  # Debugging line if no users are found
    else:
        form = PasswordResetRequestForm()
        print("Rendering form for GET request")  # Debugging line for GET request
    return render(request, "password_reset_form.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                login(request, user)
                return redirect("app_login")
        else:
            form = SetPasswordForm(user)
        return render(request, "password_reset_confirm.html", {"form": form})
    else:
        return render(request, "password_reset_invalid.html")


def home(request):
    user_type = None
    if request.user.is_authenticated:
        if hasattr(request.user, 'staff'):
            user_type = 'staff'
        elif hasattr(request.user, 'customer'):
            user_type = 'customer'
    context = {
        "user_type":user_type
    }
    return render(request, 'home.html', context)

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
                
                user.email = customerform.cleaned_data['email']
                user.save()

                customer=customerform.save(commit=False)
                customer.user=user
                customer.is_active=True 
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
                print("Invalid username or password.")
        else:
            print("Form Errors!")

    context={
        'loginform': loginform
    }
    return render(request, 'login.html', context)

def app_logout(request):
    logout(request)
    return redirect('app_login')