# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from common.models import Complaint
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User  # Adjust if you're using a custom User model

class ComplaintForm(ModelForm):
    name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name',
            'readonly': 'readonly'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email',
            'readonly': 'readonly'
        })
    )
    complaint = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe your complaint here...',
            'required': 'required'
        })
    )
    class Meta:
        model = Complaint
        fields = ['name', 'email', 'complaint']

   
