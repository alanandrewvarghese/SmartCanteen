from django.shortcuts import render
from common.decorators import *

# Create your views here.

@staff_required
def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')

@staff_required
def manage_item(request):
    return render(request, 'manage_item.html')

@staff_required
def manage_staff(request):
    return render(request, 'manage_staff.html')

@staff_required
def add_item(request):
    return render(request, 'add_item.html')