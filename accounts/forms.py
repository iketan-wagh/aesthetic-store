from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile, Address


class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-input'}))
    username = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Choose Username', 'class': 'form-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password (min. 6 chars)', 'class': 'form-input'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-input'}))
    newsletter = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username or Email', 'class': 'form-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-input'}))


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 98765 43210'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'A little about you...'}), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'address_line1', 'address_line2', 'landmark', 'city', 'state', 'pincode', 'address_type', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '10-digit mobile number'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Flat, House no., Building, Apartment'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Area, Street, Sector, Village'}),
            'landmark': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'E.g. Near Indiranagar Metro'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'State'}),
            'pincode': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '6-digit PIN code'}),
            'address_type': forms.Select(attrs={'class': 'form-input'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'rounded text-amber-900 focus:ring-amber-800'}),
        }
