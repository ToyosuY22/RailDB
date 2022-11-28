from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError

from home.models import EmailToken


class EmailTokenForm(forms.ModelForm):
    """Eメールトークン作成（一般）
    """
    class Meta:
        model = EmailToken
        fields = ['email']


class EmailTokenUniqueForm(forms.ModelForm):
    """Eメールトークン作成（既存ユーザーとのアドレス重複チェック付き）
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
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html()
    )

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class PasswordResetForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = []

    password = forms.CharField(
        label='パスワード',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html()
    )

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class PasswordUpdateForm(forms.Form):
    """SetPasswordForm を参考に作成

    https://github.com/django/django/blob/f0c06f8ab7904e1fd082f2de57337f6c7e05f177/django/contrib/auth/forms.py#L353
    """
    error_messages = {
        'password_incorrect': 'パスワードが合致しません。もう一度入力してください。'
    }

    old_password = forms.CharField(
        label='古いパスワード',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'current-password', 'autofocus': True}
        ),
    )

    new_password = forms.CharField(
        label='新しいパスワード',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        password_validation.validate_password(password, self.user)
        return password

    def save(self, commit=True):
        password = self.cleaned_data['new_password']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class UpdateUserStaffForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'display_name', 'is_active']
