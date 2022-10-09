"""認証

原則: auth.py はログイン前／profile.py はログイン後の処理を記述
"""

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth import views as auth_views
from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse_lazy
from django.views import generic
from home import forms
from home.models import EmailToken
from raildb.mixins import CheckEmailTokenMixin
from raildb.tasks import send_email


class SigninView(auth_views.LoginView):
    """ログイン
    """
    template_name = 'home/auth/signin.html'
    next_page = reverse_lazy('home:index')

    def form_valid(self, form):
        # ログイン
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'{self.request.user} さんのアカウントでログインしました！'
        )

        return response

    def form_invalid(self, form):
        # ユーザー名／パスワードについてエラーを登録
        form.add_error('username', ValidationError('', code='invalid'))
        form.add_error('password', ValidationError('', code='invalid'))

        return super().form_invalid(form)


class SignupEmailView(generic.CreateView):
    """アカウント新規登録（Eメールアドレス入力）
    """
    template_name = 'home/auth/signup_email.html'
    model = EmailToken
    form_class = forms.EmailTokenUniqueForm
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        # 種別を登録
        form.instance.kind = EmailToken.KindChoices.SIGNUP

        # Eメールトークンを作成
        response = super().form_valid(form)

        # Email を送信
        send_email(
            'アカウント新規登録の手続きを続行してください',
            form.instance.email,
            'home/mails/auth_signup_email.txt',
            {'email_token': self.object},
        )

        # 成功メッセージを追加
        messages.warning(
            self.request,
            'アカウント新規登録用Eメールを送信しました。'
            'メールの指示に従い、手続きを続けてください。'
        )

        return response


class SignupView(CheckEmailTokenMixin, generic.CreateView):
    """アカウント新規登録
    """
    template_name = 'home/auth/signup.html'
    model = get_user_model()
    form_class = forms.SignupForm
    success_url = reverse_lazy('home:index')
    email_token_kind = EmailToken.KindChoices.SIGNUP

    def form_valid(self, form):
        with transaction.atomic():
            # メールアドレスを指定
            form.instance.email = self.email_token.email

            # ユーザーを新規作成
            response = super().form_valid(form)

            # Eメールトークンを無効化
            self.email_token.use()

        # Email を送信
        send_email(
            'アカウントを新規登録しました',
            form.instance.email,
            'home/mails/auth_signup.txt',
            {'user': self.object},
        )

        # ログインを実施
        login(self.request, self.object)

        # 成功メッセージを追加
        messages.success(self.request, 'アカウントを新規登録し、ログインしました！')

        return response


class SignoutView(auth_views.LogoutView):
    """ログアウト
    """
    next_page = reverse_lazy('home:index')

    def post(self, request, *args, **kwargs):
        # ログアウト
        response = super().get(request, *args, **kwargs)
        # 成功メッセージを追加
        messages.success(self.request, 'ログアウトしました！')
        return response


class PasswordResetEmailView(generic.FormView):
    """パスワード再設定（Eメールアドレス入力）
    """
    template_name = 'home/auth/password_reset_email.html'
    form_class = forms.EmailTokenForm
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        # 該当する有効なユーザーが存在しない場合はメールを送信しない
        user_model = get_user_model()

        if user_model.objects.filter(
            email=form.instance.email,
            is_active=True
        ).exists():
            # 種別を登録
            form.instance.kind = EmailToken.KindChoices.PASSWORD_RESET

            # Eメールトークンを作成
            form.instance.save()

            # Email を送信
            send_email(
                'パスワード再設定の手続きを続行してください',
                form.instance.email,
                'home/mails/auth_password_reset_email.txt',
                {'email_token': form.instance},
            )

        # 成功メッセージを追加
        messages.warning(
            self.request,
            'パスワード再設定用Eメールを送信しました。'
            'メールの指示に従い、手続きを続けてください。'
            'ただし、該当するユーザーが存在しない場合はメールが送信されません。'
        )

        return super().form_valid(form)


class PasswordResetView(CheckEmailTokenMixin, generic.UpdateView):
    """パスワード再設定
    """
    template_name = 'home/auth/password_reset.html'
    model = get_user_model()
    form_class = forms.PasswordResetForm
    success_url = reverse_lazy('home:index')
    email_token_kind = EmailToken.KindChoices.PASSWORD_RESET

    def get_object(self):
        # Eメールトークンからユーザーを取得
        user_model = get_user_model()
        user = user_model.objects.get(email=self.email_token.email)
        return user

    def form_valid(self, form):
        with transaction.atomic():
            # パスワードを保存
            response = super().form_valid(form)

            # Eメールトークンを無効化
            self.email_token.use()

        # Email を送信
        send_email(
            'パスワードを再設定しました',
            self.object.email,
            'home/mails/auth_password_reset.txt',
            {'user': self.object},
        )

        # 成功メッセージを追加
        messages.success(self.request, 'パスワードを再設定しました！')

        return response
