from django.shortcuts import render
from common.decorators import *

# Create your views here.

@customer_required
def customer_dashboard(request):
    return render(request, 'customer_dashboard.html')

@customer_required
def view_cart(request):
    return render(request, 'view_cart.html')

@customer_required
def customer_notifications(request):
    return render(request, 'customer_notifications.html')

@customer_required
def view_orders(request):
    return render(request, 'view_orders.html')

@customer_required
def khattabook(request):
    return render(request, 'khattabook.html')

@customer_required
def raise_issue(request):
    return render(request, 'raise_issue.html')