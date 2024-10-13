from django.urls import path
from . import views

urlpatterns = [
    path('customer_dashboard/',views.customer_dashboard,name='customer_dashboard'),
    path('view_cart/',views.view_cart,name='view_cart'),
    path('customer_notifications/',views.customer_notifications,name='customer_notifications'),
    path('view_orders/',views.view_orders,name='view_orders'),
    path('place_order/',views.place_order,name='place_order'),
    path('khattabook/',views.khattabook,name='khattabook'),
    path('raise_issue/',views.raise_issue,name='raise_issue'),
    path('cart/add/<int:item_id>/',views.add_to_cart,name="add_to_cart"),
    path('cart/delete/<int:item_id>/',views.delete_from_cart,name="delete_from_cart"),

]