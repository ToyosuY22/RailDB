from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from raildb.tasks import send_email

from home import forms
from home.models import EmailToken


class IndexView(generic.TemplateView):
    """ホーム
    """
    template_name = 'home/index.html'


class SigninView(auth_views.LoginView):
    """ログイン
    """
    template_name = 'home/signin.html'
    next_page = reverse_lazy('home:index')

    def form_valid(self, form):
        # 成功メッセージを追加
        messages.success(self.request, 'ログインしました！')
        return super().form_valid(form)

    def form_invalid(self, form):
        # ユーザー名／パスワードについてエラーを登録
        form.add_error('username', ValidationError('', code='invalid'))
        form.add_error('password', ValidationError('', code='invalid'))
        return super().form_invalid(form)


class SignupEmailView(generic.FormView):
    """アカウント新規登録（Eメールアドレス入力）
    """
    template_name = 'home/signup_email.html'
    form_class = forms.SignupEmailForm
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        # 種別を登録
        form.instance.kind = EmailToken.KindChoices.SIGNUP

        # Eメールトークンを作成
        form.instance.save()

        # Email を送信
        send_email(
            'アカウント新規登録の手続きを続行してください',
            form.instance.email,
            'home/mails/signup_email.txt',
            {'token': form.instance},
        )

        # 成功メッセージを追加
        messages.warning(
            self.request,
            'アカウント新規登録用Eメールを送信しました。'
            'メールの指示に従い、手続きを続けてください。'
        )

        return super().form_valid(form)


class SignupView(generic.FormView):
    """アカウント新規登録
    """
    template_name = 'home/signup.html'
    form_class = forms.SignupForm
    success_url = reverse_lazy('home:index')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Eメールトークンを取得
        token = \
            get_object_or_404(EmailToken, id=kwargs.get('token_id'))

        # 有効性を判定
        if token.validate(EmailToken.KindChoices.SIGNUP):
            self.token = token
        else:
            # token が見つかっても無効だった場合は 404
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Eメールトークンを辞書に追加
        context.update({'token': self.token})
        return context

    def form_valid(self, form):
        # パスワードを検証
        try:
            validate_password(form.cleaned_data.get('password', form.instance))
        except ValidationError as e:
            form.add_error('password', e)
            return super().form_invalid(form)

        with transaction.atomic():
            # メールアドレスを指定
            form.instance.email = self.token.email

            # パスワードを設定
            form.instance.set_password(form.cleaned_data.get('password'))

            # ユーザーを新規作成
            form.instance.save()

            # Eメールトークンを無効化
            self.token.is_used = True
            self.token.save()

        # Email を送信
        send_email(
            'アカウントを新規登録しました',
            form.instance.email,
            'home/mails/signup.txt',
            {'user': form.instance},
        )

        # ログインを実施
        login(self.request, form.instance)

        # 成功メッセージを追加
        messages.success(self.request, 'アカウントを新規登録し、ログインしました！')

        return super().form_valid(form)


class SignoutView(auth_views.LogoutView):
    """ログアウト
    """
    next_page = reverse_lazy('home:index')

    def get(self, request, *args, **kwargs):
        # 成功メッセージを追加
        messages.success(request, 'ログアウトしました！')
        return super().get(request, *args, **kwargs)


class PWResetEmailView(generic.FormView):
    """パスワード再設定（Eメールアドレス入力）
    """
    template_name = 'home/pwreset_email.html'
    form_class = forms.PWResetEmailForm
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        # 該当する有効なユーザーが存在しない場合はメールを送信しない
        user_model = get_user_model()

        if user_model.objects.filter(
            email=form.instance.email,
            is_active=True
        ).exists():
            # 種別を登録
            form.instance.kind = EmailToken.KindChoices.PWRESET

            # Eメールトークンを作成
            form.instance.save()

            # Email を送信
            send_email(
                'パスワード再設定の手続きを続行してください',
                form.instance.email,
                'home/mails/pwreset_email.txt',
                {'token': form.instance},
            )

        # 成功メッセージを追加
        messages.warning(
            self.request,
            'パスワード再設定用Eメールを送信しました。'
            'メールの指示に従い、手続きを続けてください。'
            'ただし、該当するユーザーが存在しない場合はメールが送信されません。'
        )

        return super().form_valid(form)


class PWResetView(generic.FormView):
    """パスワード再設定
    """
    template_name = 'home/pwreset.html'
    form_class = forms.PWResetForm
    success_url = reverse_lazy('home:index')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Eメールトークンを取得
        token = \
            get_object_or_404(EmailToken, id=kwargs.get('token_id'))

        # 有効性を判定
        if token.validate(EmailToken.KindChoices.PWRESET):
            self.token = token
        else:
            # token が見つかっても無効だった場合は 404
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Eメールトークンを辞書に追加
        context.update({'token': self.token})
        return context

    def form_valid(self, form):
        # Eメールトークンからユーザーを取得
        user_model = get_user_model()
        user = user_model.objects.get(email=self.token.email)

        # パスワードを検証
        try:
            validate_password(form.cleaned_data.get('password', user))
        except ValidationError as e:
            form.add_error('password', e)
            return super().form_invalid(form)

        with transaction.atomic():
            # パスワードを設定
            user.set_password(form.cleaned_data.get('password'))
            user.save()

            # Eメールトークンを無効化
            self.token.is_used = True
            self.token.save()

        # Email を送信
        send_email(
            'パスワードを再設定しました',
            self.token.email,
            'home/mails/pwreset.txt',
            {'user': user},
        )

        # 成功メッセージを追加
        messages.success(self.request, 'パスワードを再設定しました！')

        return super().form_valid(form)
