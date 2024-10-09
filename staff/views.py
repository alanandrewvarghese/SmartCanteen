from django.shortcuts import render
from common.decorators import *

# Create your views here.

@staff_required
def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')

@staff_required
def manage_item(request):
    return render(request, 'manage_item.html')