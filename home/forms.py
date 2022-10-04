from django import forms
from django.contrib.auth import get_user_model, password_validation

from home.models import EmailToken


class EmailTokenForm(forms.ModelForm):
    """Eメールトークン作成
    """
    class Meta:
        model = EmailToken
        fields = ['email']


class SignupForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['display_name']

    password = forms.CharField(
        label='パスワード',
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html()
    )
