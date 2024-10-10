from django.urls import path
from . import views

urlpatterns = [
    path('staff_dashboard/',views.staff_dashboard,name='staff_dashboard'),
    path('manage_item/',views.manage_item,name='manage_item'),
    path('manage_staff/',views.manage_staff,name='manage_staff'),
    path('add_item/',views.add_item,name='add_item'),

    
]