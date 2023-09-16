from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class registrationform(UserCreationForm):
    email = forms.EmailField(max_length=100, required=True, help_text='Required. Enter a valid email address.')
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(registrationform, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
        return user

class loginform(AuthenticationForm):
    username = forms.CharField(max_length=100, required=True, help_text='Required. Enter your username or email.')
    password = forms.CharField(widget=forms.PasswordInput, required=True, help_text='Required. Enter your password.')

    class Meta:
        model = User

