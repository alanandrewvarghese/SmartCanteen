from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


def to_title_case(text):
    return text.title()

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=100,unique=True)
    name = models.CharField(max_length=50)
    has_khatta = models.BooleanField(default=False)

    def __str__(self):
        return f"Customer: {self.name} ({self.email})"


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100,unique=True)

    def __str__(self):
        return f"Staff: {self.name} ({self.phone})"

class Item(models.Model):
    CATEGORY_CHOICES = [
        ("BF","Breakfast"),
        ("LN","Lunch"),
        ("SK","Snacks"),
        ("DS","Desserts"),
        ("DR","Drinks"),
        ("CR","Curry"),
    ]

    FOOD_CHOICES = [
        ("VG","Vegetarian"),
        ("NG","Non Vegetarian"),
    ]

    item_id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=40)
    price = models.DecimalField(max_digits=7,decimal_places=2)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    food_type = models.CharField(max_length=2, choices=FOOD_CHOICES)
    item_image = models.ImageField(upload_to='items/')
    quantity = models.IntegerField(default=0,validators=[MinValueValidator(0)])


    def __str__(self):
        return f"{self.item_name} : {self.price} INR"
    
    def save(self, *args, **kwargs):
        # Convert text to title case before saving
        self.item_name = to_title_case(self.item_name)
        super().save(*args, **kwargs)

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='orders')
    ordered_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=8,decimal_places=2, null=True)
    payment_status = models.CharField(max_length=10, default="failed")

    class Meta:
        ordering = ['-ordered_at']

    def __str__(self):
        return f"Order #{self.order_id} | at {self.ordered_at} | Status: {self.payment_status}"

class OrderItem(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    class Meta:
        unique_together = ('item', 'order')

    def __str__(self):
        return f"{self.quantity} x {self.item} in Order #{self.order.order_id}"


class KhattaBook(models.Model):
    user = models.OneToOneField(Customer,on_delete=models.CASCADE,null=True,blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE ,related_name='khattabook_order')
    pending_payment = models.DecimalField(max_digits=8,decimal_places=2)
    status = models.CharField(max_length=20,default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"KhattaBook of {self.user} | Total: ${self.pending_payment}"



class Notification(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_notification')
    message = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} | {self.message[:50]}..."


class Complaint(models.Model):
    user = models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='user_complaints')
    complaint = models.CharField(max_length=600)
    status = models.CharField(max_length=20, default='pending')
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint from {self.user.name} | Status: {self.status}"
    
class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.customer.name} | Created at {self.created_at}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1,validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('cart', 'item')

    def __str__(self):
        return f"{self.quantity} x {self.item.item_name} in Cart of {self.cart.customer.name}"