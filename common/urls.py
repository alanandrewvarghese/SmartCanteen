from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('register/',views.customer_registration,name='customer_registration'),
    path('login/',views.app_login,name='app_login'),
    path('logout/',views.app_logout,name='app_logout'),

]