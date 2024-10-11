from django.shortcuts import render, get_object_or_404
from common.decorators import *
from staff.forms import ItemCreationForm, StaffCreationForm
from common.forms import CreateUserForm
from common.models import Item

# Create your views here.

@staff_required
def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')

@staff_required
def manage_item(request):
    items = Item.objects.all()
    context = {
        "items":items
    }
    return render(request, 'manage_item.html', context)

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

# @staff_required
# def update_item(request,item_id):
#     item = get_object_or_404(Item, pk=item_id)

#     if request.method == 'POST':
#         # Pass the instance of the item to update
#         itemcreationform = ItemCreationForm(request.POST, request.FILES, instance=item)
#         if itemcreationform.is_valid():
#             itemcreationform.save()  # Save the updated item
#             return redirect('manage_item')  # Redirect to the manage items page
#         else:
#             print("Invalid form")
#     else:
#         # Pre-fill the form with the existing item's data
#         itemcreationform = ItemCreationForm(instance=item)

#     context = {
#         "itemcreationform": itemcreationform,
#         "item": item
#     }
#     return render(request, 'update_item.html', context)

@staff_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('manage_item')


@staff_required
def add_staff(request):
    userform=CreateUserForm()
    staffform=StaffCreationForm()

    if request.method=='POST':
        userform=CreateUserForm(request.POST)
        staffform=StaffCreationForm(request.POST)
        if userform.is_valid() and staffform.is_valid():
            user=userform.save()
            staff=staffform.save(commit=False)
            staff.user=user 
            staff.save()
            return redirect('app_login')
    context={
        'userform':userform,
        'staffform':staffform,
    }
    return render(request, 'add_staff.html', context)

@staff_required
def update_stock(request):
    return render(request, 'update_stock.html')

@staff_required
def staff_notification(request):
    return render(request, 'staff_notification.html')

@staff_required
def manage_customers(request):
    return render(request, 'manage_customers.html')

@staff_required
def manage_khattabook(request):
    return render(request, 'manage_khattabook.html')

@staff_required
def manage_accounts(request):
    return render(request, 'manage_accounts.html')

@staff_required
def manage_issues(request):
    return render(request, 'manage_issues.html')