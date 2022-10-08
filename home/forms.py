from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django_select2 import forms as s2forms

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
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html()
    )


class PasswordResetForm(forms.Form):
    password = forms.CharField(
        label='パスワード',
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html()
    )


class UpdateDisplayNameForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['display_name']


class UpdatePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='現在のパスワード',
        strip=False,
        widget=forms.PasswordInput()
    )

    new_password = forms.CharField(
        label='新しいパスワード',
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html()
    )


class DeleteUserForm(forms.Form):
    check = forms.CharField(
        label='入力欄',
        help_text='"delete" と入力してください',
        max_length=20
    )

    def clean_check(self):
        # 値を取得
        check = self.cleaned_data.get('check')

        # 入力値が間違っていた場合は拒否
        if check != 'delete':
            raise ValidationError(
                '入力値が誤っています', code='invalid'
            )

        # 問題なければ入力された値をそのまま帰す
        return check


class RegisterStaffForm(forms.Form):
    email = forms.EmailField(label='Eメールアドレス')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_model = get_user_model()

        # 該当するユーザーが存在しない場合は拒否
        if not user_model.objects.filter(email=email).exists():
            raise ValidationError(
                '該当するユーザーが存在しません', code='invalid'
            )

        # 該当するユーザーが存在するが、すでにスタッフの場合は拒否
        user = user_model.objects.get(email=email)
        if user.is_staff:
            raise ValidationError(
                'すでにこのユーザーはスタッフです', code='invalid'
            )

        # 問題なければ入力された値をそのまま帰す
        return email


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

    class PermissionMultipleChoiceField(forms.ModelMultipleChoiceField):
        widget = forms.widgets.CheckboxSelectMultiple()

        def label_from_instance(self, obj):
            # 権限の name を選択肢として表示
            return obj.name

    class UserSelect2MultipleWidgetWidget(s2forms.ModelSelect2MultipleWidget):
        search_fields = [
            'email__startswith'
        ]

    # raildb からはじまる codename のみ選択肢として表示
    permissions = PermissionMultipleChoiceField(
        label='権限',
        queryset=Permission.objects.filter(codename__startswith='raildb')
    )

    # スタッフを選択肢として表示
    user_model = get_user_model()
    user_list = forms.ModelMultipleChoiceField(
        label='メンバー',
        help_text='スタッフのメールアドレスを入力してください',
        widget=UserSelect2MultipleWidgetWidget(),
        queryset=user_model.objects.filter(is_staff=True)
    )
