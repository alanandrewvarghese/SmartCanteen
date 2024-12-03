from django.shortcuts import render, get_object_or_404
from common.decorators import *
from django.contrib.auth.models import User
from django.db.models import Sum, Count, F
from django.db.models.functions import Coalesce
from staff.forms import ItemCreationForm, StaffCreationForm, StockUpdationForm
from common.forms import CreateUserForm
from common.models import Item, Order, OrderItem,Customer,Staff,Complaint,Notification,KhattaBook
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import ListView
from django.contrib import messages

# Create your views here.

@staff_required
def staff_dashboard(request):
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


def chart_data(request):
    resultMostPopular = (
    OrderItem.objects.values('item__item_name')  
    .annotate(total_quantity=Sum('quantity'))   
    .order_by('-total_quantity')                 
    )[:5]

    resultLeastPopular = (
    OrderItem.objects.values('item__item_name')  
    .annotate(total_quantity=Sum('quantity'))   
    .order_by('total_quantity')                 
    )[:5]  
    
    item_namesMP = [entry['item__item_name'] for entry in resultMostPopular]
    quantitiesMP = [entry['total_quantity'] for entry in resultMostPopular]
    
    item_namesLP = [entry['item__item_name'] for entry in resultLeastPopular]
    quantitiesLP = [entry['total_quantity'] for entry in resultLeastPopular]

    labels_mp = item_namesMP
    data_mp = quantitiesMP

    labels_lp = item_namesLP
    data_lp = quantitiesLP

    return JsonResponse({'labels_mp': labels_mp,'data_mp':data_mp,'labels_lp':labels_lp,'data_lp':data_lp})


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


@staff_required
def manage_customers(request):
    customers=Customer.objects.all()

    context={
        'customers': customers
    }
    return render(request, 'manage_customers.html', context)


@staff_required
def remove_customers(request,customer_id):
    try:
        customer=Customer.objects.get(pk=customer_id)
        User.objects.filter(customer=customer).delete()
    except Exception as e:
        print(f"Error: {e}")
    
    return redirect(manage_customers)


@staff_required
def update_customer_status(request,customer_id):
    try:
        customer=Customer.objects.get(pk=customer_id)
        if customer.is_active:
            customer.is_active=False
        else:
            customer.is_active=True
        customer.save()
        
    except Exception as e:
        print(f"Error: {e}")
    
    return redirect(manage_customers)


@staff_required
def manage_khattabook(request):
    khattabooks = KhattaBook.objects.select_related('user').all()
    
    return render(request, 'manage_khattabook.html', {
        'khattabooks': khattabooks,
    })


@staff_required
def manage_accounts(request):
    orders = Order.objects.prefetch_related('items__item').annotate(
        total_price=Sum(F('items__item__price') * F('items__quantity'))
    ).order_by('-order_id')

    context = {
        'orders': orders
    }

    return render(request, 'manage_accounts.html', context)


@staff_required
def manage_issues(request):
    complaints=Complaint.objects.filter(status="pending")
    context={
        "complaints": complaints
    }
    return render(request, 'manage_issues.html', context)


@staff_required
def response_message(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    
    if request.method == 'POST':
        message = request.POST.get('response_message', '').strip()
        
        if message: 
            complaint.response = message
            complaint.status = 'responded' 
            complaint.save()
            
            Notification.objects.create(
                user=complaint.user.user,
                message=f"Your complaint [{complaint.complaint}] has been responded to: {message}",
            )
            
            messages.success(request, "Response sent successfully and notification created.")
        else:
            messages.error(request, "Response message cannot be empty.")
    
    return redirect('manage_issues')