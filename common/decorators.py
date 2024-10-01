from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return redirect('app_login')  # Redirect to login if user is not authenticated

        # Check if the authenticated user is a staff member
        if hasattr(request.user, 'staff'):
            return view_func(request, *args, **kwargs)
        else:
            # Return forbidden response or render a custom "403 Forbidden" page
            return HttpResponseForbidden('You are not authorized to access this page.')
    return _wrapped_view

def customer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return redirect('app_login')  # Redirect to login if user is not authenticated

        # Check if the authenticated user is a staff member
        if hasattr(request.user, 'customer'):
            return view_func(request, *args, **kwargs)
        else:
            # Return forbidden response or render a custom "403 Forbidden" page
            return HttpResponseForbidden('You are not authorized to access this page.')
    return _wrapped_view