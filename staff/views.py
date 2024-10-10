from django.shortcuts import render
from common.decorators import *
from staff.forms import ItemCreationForm

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
    if request.method == 'POST':
        itemcreationform = ItemCreationForm(request.POST, request.FILES)
        if itemcreationform.is_valid():
            itemcreationform.save()
            return redirect('manage_item')
        else:
            print("Invalid form")
    else:
        itemcreationform = ItemCreationForm()

    context = {
        "itemcreationform": itemcreationform
    }
    return render(request, 'add_item.html',context)

@staff_required
def add_staff(request):
    return render(request, 'add_staff.html')

@staff_required
def update_stock(request):
    return render(request, 'update_stock.html')