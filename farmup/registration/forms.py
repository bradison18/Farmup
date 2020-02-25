from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=100,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',}))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )

    def clean_email(self):

        cleaned_data = super().clean()
        email = cleaned_data.get("email")

        email_qset = User.objects.filter(email=email)

        if email_qset.exists():
            raise forms.ValidationError('Email is taken already')
        return email

    def clean_username(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")

        user_qset = User.objects.filter(username=username)

        if user_qset.exists():
            raise forms.ValidationError('User name is taken already')
        return username

    def clean_confirm_password(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Passwords did not match')
            return confirm_password
        return confirm_password


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': "input100", 'placeholder': 'Email Id'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "input100", 'placeholder': 'Password'}))

    def clean_emailid(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        email_set = User.objects.filter(email=email)

        if not email_set.exists():
            raise forms.ValidationError('Email is not registered')
        else:
            user = User.objects.get(email=email)
            if not user.is_active:
                raise forms.ValidationError('User not authenticated')
        return email

    def clean_password(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        email_set = User.objects.filter(email=email)

        if email_set.exists():
            password = cleaned_data.get('password')
            user = User.objects.get(email=email)
            userlog = authenticate(username=user, password=password)
            if userlog is None:
                raise forms.ValidationError('Invalid password')
            return password
