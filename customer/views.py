from django.shortcuts import render
from common.decorators import *

# Create your views here.

@customer_required
def customer_dashboard(request):
    return render(request, 'customer_dashboard.html')

@customer_required
def view_cart(request):
    return render(request, 'view_cart.html')