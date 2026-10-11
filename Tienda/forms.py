from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria',
                  'imagen', 'peso_kg', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este email.')
        return email


class LoginForm(AuthenticationForm):
    """Primer factor: usuario y contraseña."""

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': 'Usuario o contraseña incorrectos.',
    }
