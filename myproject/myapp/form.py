from django import forms
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    # Add any additional fields if needed
    email = forms.EmailField()

    class Meta:
        # model = user  # Replace 'User' with your custom user model if you have one
        fields = ['username', 'email', 'password1', 'password2']


from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    pass
