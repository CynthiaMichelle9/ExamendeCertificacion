from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=50,
        required=True,
        label='Correo Electrónico',
        error_messages={'required': 'El correo electrónico es obligatorio'},
        widget=forms.EmailInput(attrs={'placeholder': 'Ingrese su correo electrónico'})
    )
    password = forms.CharField(
        max_length=16,
        required=True,
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'}),
        error_messages={'required': 'La contraseña es obligatoria'}
    )

    class Meta:
        model = User


class RegistroForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        help_text='Requerido. 30 caracteres o menos. Letras y números solamente.',
        label='Nombre de usuario:',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu nombre de usuario'})
    )

    email = forms.EmailField(
        max_length=254,
        label='Correo electrónico:',
        help_text='Requerido. Ingrese una dirección de correo válida.',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu correo electrónico'})
    )

    email2 = forms.EmailField(
        max_length=254,
        help_text='Requerido. Ingrese una dirección de correo válida.',
        label='Confirmar correo electrónico:',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Confirma tu correo electrónico'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        email2 = cleaned_data.get('email2')

        if email != email2:
            raise forms.ValidationError(
                'Los correos electrónicos no coinciden. Por favor, inténtelo de nuevo.')

    class Meta:
        model = User
        fields = ('username', 'email', 'email2')

