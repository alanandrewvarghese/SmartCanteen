from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('register/',views.customer_registration,name='customer_registration'),
    path('login/',views.app_login,name='app_login'),
    path('logout/',views.app_logout,name='app_logout'),
    path("password_reset/", views.password_reset_request, name="password_reset"),
    path("reset/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
]