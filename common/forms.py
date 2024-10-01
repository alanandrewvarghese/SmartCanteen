from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import *

class CreateUserForm(UserCreationForm):
    username = forms.CharField(
        label = 'Username',
        widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
    )
    password1 = forms.CharField(
        label = 'Password',
        widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )
    password2 = forms.CharField(
        label = 'Confirm Password',
        widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter your password'})
    )

    class Meta:
        model = User
        fields = ['username','password1','password2']



class CreateCustomerForm(ModelForm):

    name = forms.CharField(
        label = 'Name',
        widget = forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter your full name'}),
    )

    email = forms.EmailField(
        label = 'Email Address',
        widget = forms.EmailInput(attrs={'class': 'form-control','placeholder':'Enter your Email id'}),
    )

    has_khatta = forms.BooleanField(
        label ='KhattaBook Required',
        widget = forms.CheckboxInput(attrs={'class': 'form-check-input has-khatta'}),
        required=False
    )

    class Meta:
        model = Customer
        fields = ['name', 'email', 'has_khatta']


class AppLoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
    )