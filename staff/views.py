from django.shortcuts import render, get_object_or_404
from common.decorators import *
from django.db.models import Sum, Count, F
from django.db.models.functions import Coalesce
from staff.forms import ItemCreationForm, StaffCreationForm, StockUpdationForm
from common.forms import CreateUserForm
from common.models import Item, Order, OrderItem,Customer,Staff,Complaint,Notification

# Create your views here.

@staff_required
def staff_dashboard(request):
    # Fetching all orders with related order items and calculating total price for each order
    orders = Order.objects.prefetch_related('items__item').annotate(
        total_price=Sum(F('items__item__price') * F('items__quantity'))
    ).order_by('-order_id')
    
    dashboard_data = {
        'total_orders': Order.objects.count(),
        'total_customers': Customer.objects.count(),
        'total_revenue': orders.aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0,
        'successful_orders': Order.objects.filter(payment_status='success').count()
    }

    context = {
        'orders': orders,
        'data': dashboard_data
    }
    
    return render(request, 'staff_dashboard.html', context)
@staff_required
def manage_item(request):
    items = Item.objects.all()
    context = {
        "items":items
    }
    return render(request, 'manage_item.html', context)

@staff_required
def manage_staff(request):
    staff_details=Staff.objects.all()

    context = {
        'staff_details': staff_details
    }
    return render(request, 'manage_staff.html', context)

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
def update_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'POST':
        form = ItemCreationForm(request.POST, request.FILES, instance=item)
        
        if form.is_valid():
            form.save()
            return redirect('manage_item')  
    else:
        form = ItemCreationForm(instance=item)

    context = {
        "form": form,
        "item": item
    }

    return render(request, 'update_item.html', context)


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
    form=StockUpdationForm()
    if request.method=='POST':
        item_id=request.POST['item_id']
        item=get_object_or_404(Item,pk=item_id)

        form=StockUpdationForm(request.POST)
        if form.is_valid():
            stock=form.cleaned_data['stock']
            item.quantity=stock
            item.save()
            return redirect('update_stock')
        else:
            print("Invalid Form")
        
    items = Item.objects.all()

    context={
        'form':form,
        'items':items
    }
    return render(request, 'update_stock.html', context)

@staff_required
def staff_notification(request):
    staff_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'staff_notification.html',{
        'notifications':staff_notifications
    })


    return render(request, 'staff_notification.html')

@staff_required
def manage_customers(request):
    customers=Customer.objects.all()

    context={
        'customers': customers
    }
    return render(request, 'manage_customers.html', context)

@staff_required
def manage_khattabook(request):
    return render(request, 'manage_khattabook.html')

@staff_required
def manage_accounts(request):
    return render(request, 'manage_accounts.html')

@staff_required
def manage_issues(request):
    complaints=Complaint.objects.all()
    context={
        "complaints": complaints
    }
    return render(request, 'manage_issues.html', context)


