from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError

from home.models import EmailToken


class SignupEmailForm(forms.ModelForm):
    """Eメールトークン作成（アカウント新規登録）
    """
    class Meta:
        model = EmailToken
        fields = ['email']

    def clean_email(self):
        # 値を取得
        email = self.cleaned_data.get('email')

        # すでにEメールアドレスが使用されていた場合は拒否
        user_model = get_user_model()
        if user_model.objects.filter(email=email).exists():
            raise ValidationError(
                'このEメールアドレスはすでに使用されています', code='invalid'
            )

        # 問題なければ入力された値をそのまま帰す
        return email


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


class PWResetEmailForm(forms.ModelForm):
    """Eメールトークン作成（パスワード再設定）　
    """
    class Meta:
        model = EmailToken
        fields = ['email']


class PWResetForm(forms.Form):
    password = forms.CharField(
        label='パスワード',
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html()
    )
