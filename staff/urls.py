from django.urls import path
from . import views

urlpatterns = [
    path('staff_dashboard/',views.staff_dashboard,name='staff_dashboard'),
    path('manage_item/',views.manage_item,name='manage_item'),

    
]