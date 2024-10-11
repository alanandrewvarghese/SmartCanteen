from django.urls import path
from . import views

urlpatterns = [
    path('staff_dashboard/',views.staff_dashboard,name='staff_dashboard'),
    path('manage_item/',views.manage_item,name='manage_item'),
    path('manage_staff/',views.manage_staff,name='manage_staff'),
    path('add_item/',views.add_item,name='add_item'),
    path('add_staff/',views.add_staff,name='add_staff'),
    path('update_stock/',views.update_stock,name='update_stock'),
    path('staff_notification/',views.staff_notification,name='staff_notification'),
    path('item/delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('manage_customers/',views.manage_customers,name='manage_customers'),
    path('manage_khattabook/',views.manage_khattabook,name='manage_khattabook'),
    path('manage_accounts/',views.manage_accounts,name='manage_accounts'),


    

    
]