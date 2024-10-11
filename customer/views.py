from django.shortcuts import render, get_object_or_404, redirect
from common.decorators import *
from django.contrib import messages
from common.models import Item, Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

@customer_required
def customer_dashboard(request):
    items = Item.objects.all()
    context = {
        "items":items
    }
    return render(request, 'customer_dashboard.html', context)

@customer_required
def view_cart(request):
    try:
        cart = Cart.objects.get(customer=request.user.customer)
        cart_items = cart.cart_items.all()
    except ObjectDoesNotExist:
        cart_items = []  
    
    total = sum(item.item.price * item.quantity for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'view_cart.html', context)

@customer_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

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
        messages.success(request, f"{item.item_name} added to cart successfully!")
    except Exception as e:
        pass
    
    return redirect('customer_dashboard')


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