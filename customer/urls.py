from django.urls import path
from . import views

urlpatterns = [
    path('customer_dashboard/',views.customer_dashboard,name='customer_dashboard'),
    path('view_cart/',views.view_cart,name='view_cart'),
    path('customer_notifications/',views.customer_notifications,name='customer_notifications'),

]