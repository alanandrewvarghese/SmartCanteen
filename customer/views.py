from django.shortcuts import render, get_object_or_404, redirect
from common.decorators import *
from django.http import JsonResponse
from django.contrib import messages
from common.models import Item, Cart, CartItem, Order, OrderItem,Complaint,Order,Notification,KhattaBook, Customer, Staff
from django.core.exceptions import ObjectDoesNotExist
from .forms import ComplaintForm
from customer.recommendation_system import generate_recommendations
from django.db.models import Sum

# Create your views here.

@customer_required
def customer_dashboard(request):
    items_in_stock = Item.objects.filter(quantity__gt=0)
    items_out_of_stock = Item.objects.filter(quantity__lt=1)
    bf = Item.objects.filter(category='BF',quantity__gt=0)
    cr = Item.objects.filter(category='CR',quantity__gt=0)
    ln = Item.objects.filter(category='LN',quantity__gt=0)
    sk = Item.objects.filter(category='SK',quantity__gt=0)
    dr = Item.objects.filter(category='DR',quantity__gt=0)
    ds = Item.objects.filter(category='DS',quantity__gt=0)
    customer_id=request.user.customer.id

    try:
        suggested_item_ids = generate_recommendations(customer_id)
        suggested_items = Item.objects.filter(item_id__in=suggested_item_ids, quantity__gt=0)
    except Exception as e:
        suggested_items = ''
        print(f"Error: {e}")

    context = {
        "items_in_stock":items_in_stock,
        "items_out_of_stock":items_out_of_stock,
        "bf":bf,
        "cr":cr,
        "ln":ln,
        "sk":sk,
        "dr":dr,
        "ds":ds,
        "suggested_items": suggested_items
    }
    return render(request, 'customer_dashboard.html', context)

@customer_required
def view_cart(request):
    customer = request.user.customer
    staff=Staff.objects.all()
    khattabook = KhattaBook.objects.filter(user=customer)
    total_due = khattabook.filter(user=customer,status='Unpaid').aggregate(total=Sum('pending_payment'))['total'] or 0

    if (total_due >= 3000 and customer.is_active):
        for staff_member in staff:
            Notification.objects.create(
                user=staff_member.user,
                message=f"[{customer.name}] has exceeded Khattabook limit. Account has been disabled.",
            )
        customer.is_active = False
        customer.save()
    try:
        cart = Cart.objects.get(customer=request.user.customer)
        cart_items = cart.cart_items.all()
    except ObjectDoesNotExist:
        cart_items = []  
    
    is_active=request.user.customer.is_active
    
    total = sum(item.item.price * item.quantity for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total': total,
        'is_active': is_active
    }
    return render(request, 'view_cart.html', context)

@customer_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'POST':
        try:
            if not hasattr(request.user, 'customer'):
                raise ValueError("No customer associated with the user.")

            cart, created = Cart.objects.get_or_create(customer=request.user.customer)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)

            if not created:
                cart_item.quantity += 1
            else:
                cart_item.quantity = 1

            if cart_item.quantity is None or cart_item.quantity <= 0:
                raise ValueError("Quantity is invalid before saving.")

            cart_item.save()
            return JsonResponse({
                'status': 'success',
                'message': f"{item.item_name} added to cart successfully!"
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while adding the item to the cart.'
            })

    return redirect('customer_dashboard')

@customer_required
def delete_from_cart(request, item_id):
    cart = get_object_or_404(Cart, customer=request.user.customer)
    
    try:
        item = CartItem.objects.get(item_id=item_id, cart=cart)
    except CartItem.DoesNotExist:
        messages.error(request, 'Item not found in your cart.')
        return redirect('view_cart')
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, f'The item "{item.item.item_name}" has been removed from your cart.')
        return redirect('view_cart')


@customer_required
def customer_notifications(request):
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'customer_notifications.html',{
        'notifications':user_notifications
    })

@customer_required
def view_orders(request):
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer).prefetch_related('items__item')

    for order in orders:
        order.total_amount = sum(
            order_item.quantity * order_item.item.price 
            for order_item in order.items.all()
        )

    context = {
        'orders': orders
    }
    return render(request, 'view_orders.html', context)

@customer_required
def place_order(request):
    customer = request.user.customer

    cart = Cart.objects.filter(customer=customer).first()
    
    if not cart or not cart.cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('view_cart') 
    
    is_active=customer.is_active

    if is_active:
        try:
            order = Order.objects.create(customer=customer)

            order_items = [
                OrderItem(
                    order=order,
                    item=cart_item.item,
                    quantity=cart_item.quantity
                ) for cart_item in cart.cart_items.all()
            ]
            OrderItem.objects.bulk_create(order_items)

            total_amount = sum(
                order_item.quantity * order_item.item.price 
                for order_item in order.items.all()
            )

            order.total_amount = total_amount
            order.save()

            khattabook = KhattaBook.objects.create(
                user=customer,
                pending_payment = total_amount,
                status = "Unpaid",
                order = order
            )
            khattabook.save()

            cart.cart_items.all().delete()

            messages.success(request, 'Your order has been placed successfully!')
            return redirect('view_orders')  
        except Exception as e:
            print(f"Error placing order: {str(e)}")
            messages.error(request, 'An error occurred while placing your order. Please try again.')
            return redirect('view_cart')
    else:
        return redirect('view_cart')

@customer_required
def khattabook(request):
    customer = request.user.customer
    khattabook = KhattaBook.objects.filter(user=customer)
    total_due = khattabook.filter(status='Unpaid').aggregate(total=Sum('pending_payment'))['total'] or 0

    context = {
        'khattabook':khattabook,
        'total_due':total_due
    }
    return render(request, 'khattabook.html', context)

@customer_required
def khattabook_payment(request):
    customer = request.user.customer
    try:
        KhattaBook.objects.filter(user=customer,status="Unpaid").update(
            pending_payment=0,
            status="Paid"
        )
        customer.is_active = True
        customer.save()
        
    except Exception as e:
        print(f"Error updating khattabook entries: {str(e)}")

    return redirect('khattabook')

@customer_required
def raise_issue(request):
    initial_data = {'email': request.user.customer.email,'name':request.user.customer.name}  
    if request.method == 'POST':
        form = ComplaintForm(request.POST, initial=initial_data)
        if form.is_valid():
            complaint =form.save(commit = False)
            complaint.user = request.user.customer
            complaint.save()

            messages.success(request, 'Your complaint has been submitted!')
            return redirect('customer_dashboard')
    else:
        form = ComplaintForm(initial=initial_data)

    context = {
        'form':form
    }

    return render(request, 'raise_issue.html',context)