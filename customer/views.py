from django.shortcuts import render, get_object_or_404, redirect
from common.decorators import *
from django.http import JsonResponse
from django.contrib import messages
from common.models import Item, Cart, CartItem, Order, OrderItem
from django.core.exceptions import ObjectDoesNotExist

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

    context = {
        "items_in_stock":items_in_stock,
        "items_out_of_stock":items_out_of_stock,
        "bf":bf,
        "cr":cr,
        "ln":ln,
        "sk":sk,
        "dr":dr,
        "ds":ds,
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
def customer_notifications(request):
    return render(request, 'customer_notifications.html')

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
    # Get the logged-in customer's profile
    customer = request.user.customer

    # Get the cart for the logged-in customer
    cart = Cart.objects.filter(customer=customer).first()
    
    if not cart or not cart.cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('view_cart')  # Redirect to the cart view

    try:
        # Create an order and assign the customer
        order = Order.objects.create(customer=customer)

        # Create OrderItems from the cart
        order_items = [
            OrderItem(
                order=order,
                item=cart_item.item,
                quantity=cart_item.quantity
            ) for cart_item in cart.cart_items.all()
        ]
        OrderItem.objects.bulk_create(order_items)

        # Clear the cart after placing the order
        cart.cart_items.all().delete()

        messages.success(request, 'Your order has been placed successfully!')
        return redirect('view_orders')  # Redirect to view the orders

    except Exception as e:
        # Log the error (in a production environment)
        print(f"Error placing order: {str(e)}")
        messages.error(request, 'An error occurred while placing your order. Please try again.')
        return redirect('view_cart')

@customer_required
def khattabook(request):
    return render(request, 'khattabook.html')

@customer_required
def raise_issue(request):
    return render(request, 'raise_issue.html')