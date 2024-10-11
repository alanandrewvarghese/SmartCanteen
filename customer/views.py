from django.shortcuts import render, get_object_or_404, redirect
from common.decorators import *
from django.contrib import messages
from common.models import Item, Cart, CartItem, Order, OrderItem
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
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer)

    for order in orders:
        total_amount = sum(order_item.quantity * order_item.item.price for order_item in order.order_items.all())
        order.total_amount = total_amount  # Add total_amount as an attribute to the order

    context = {
        'orders': orders
    }
    return render(request, 'view_orders.html', context)

@customer_required
def place_order(request):
    # Get the logged-in customer's profile
    customer = request.user.customer

    # Get the cart for the logged-in customer
    cart = Cart.objects.filter(customer=customer).first()
    
    if not cart or not cart.cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')  # Redirect to the cart view

    # Create an order and assign the customer
    order = Order.objects.create(customer=customer)  # Add the customer here

    # Create OrderItems from the cart
    for cart_item in cart.cart_items.all():
        OrderItem.objects.create(
            order=order,
            item=cart_item.item,
            quantity=cart_item.quantity
        )

    # Clear the cart after placing the order
    cart.cart_items.all().delete()

    messages.success(request, 'Your order has been placed successfully!')
    return redirect('view_orders')  # Redirect to view the orders


@customer_required
def khattabook(request):
    return render(request, 'khattabook.html')

@customer_required
def raise_issue(request):
    return render(request, 'raise_issue.html')