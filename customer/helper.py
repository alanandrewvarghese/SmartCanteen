from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
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

def send_khatta_due_email(total_due,customer_email):
    email=customer_email
    associated_users = User.objects.filter(email=email)
    print("Number of associated users found:", associated_users.count())  
    if associated_users.exists():
        for user in associated_users:
            print(f"Processing user: {user.username}")
            email_subject = "Urgent Payment Reminder"
            email_body = render_to_string("khatta_due.html", {
                "payment_due": total_due,
            })
            text_content = f"Your account has an outstanding balance of {total_due}; please pay soon to avoid account suspension."
            email_message = EmailMultiAlternatives(
                email_subject, text_content, "smartcanteen@gmail.com", [email]
            )
            email_message.attach_alternative(email_body, "text/html")
            email_message.send()
            print(f"HTML Password reset email sent to {email}")
     
            return redirect('view_cart')
        else:
            print(f"No users found with email {email}")