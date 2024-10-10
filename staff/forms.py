from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from common.models import Item, Staff
from django.core.validators import MinValueValidator

class StaffCreationForm(ModelForm):

    name = forms.CharField(
        label='Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
    )

    phone = forms.CharField(
        label='Phone',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
    )

    class Meta:
        model = Staff
        fields = ['name', 'email', 'phone']


class ItemCreationForm(ModelForm):

    item_name = forms.CharField(
        label='Item Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Item Name'}),
    )

    price = forms.DecimalField(
        label='Price',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Price'}),
        max_digits=7,
        decimal_places=2
    )

    category = forms.ChoiceField(
        label='Category',
        choices=Item.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    food_type = forms.ChoiceField(
        label='Food Type',
        choices=Item.FOOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    item_image = forms.ImageField(
        label='Item Image',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Item
        fields = ['item_name', 'price', 'category', 'food_type', 'item_image']