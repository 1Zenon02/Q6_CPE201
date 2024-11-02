from django import forms
from .models import ProjectElement, Material

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    address = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'email', 'address', 'password1', 'password2']



class ManagerRegisterForm(UserCreationForm):
    id_number = forms.CharField(max_length=150, required=True, help_text="Required")

    class Meta:
        model = User
        fields = ['username', 'id_number', 'password1', 'password2']

class ManagerLoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput)


class ProjectElementForm(forms.ModelForm):
    class Meta:
        model = ProjectElement
        fields = ['project', 'name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
        }

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['element', 'name', 'qty', 'unit', 'price_per_qty', 'markup_percentage']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'element': forms.Select(attrs={'class': 'form-control'}),
            'qty': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'price_per_qty': forms.NumberInput(attrs={'class': 'form-control'}),
            'markup_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }