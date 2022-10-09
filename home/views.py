from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth import mixins as auth_mixins
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django_datatables_view.base_datatable_view import BaseDatatableView
from raildb.tasks import send_email

from home import forms
from home.models import EmailToken, News


class IndexView(generic.TemplateView):
    """ホーム
    """
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # お知らせ
        context['news_list'] = News.objects.all()

        return context


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
    form_class = forms.EmailTokenUniqueForm
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


class PasswordResetEmailView(generic.FormView):
    """パスワード再設定（Eメールアドレス入力）
    """
    template_name = 'home/password_reset_email.html'
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
                'home/mails/password_reset_email.txt',
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


class PasswordResetView(generic.FormView):
    """パスワード再設定
    """
    template_name = 'home/password_reset.html'
    form_class = forms.PasswordResetForm
    success_url = reverse_lazy('home:index')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Eメールトークンを取得
        token = \
            get_object_or_404(EmailToken, id=kwargs.get('token_id'))

        # 有効性を判定
        if token.validate(EmailToken.KindChoices.PASSWORD_RESET):
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
            'home/mails/password_reset.txt',
            {'user': user},
        )

        # 成功メッセージを追加
        messages.success(self.request, 'パスワードを再設定しました！')

        return super().form_valid(form)


class ProfileView(auth_mixins.LoginRequiredMixin, generic.TemplateView):
    """プロフィール
    """
    template_name = 'home/profile.html'


class UpdateEmailEmailView(auth_mixins.LoginRequiredMixin, generic.FormView):
    """Eメールアドレス変更（Eメールアドレス入力）
    """
    template_name = 'home/update_email_email.html'
    form_class = forms.EmailTokenUniqueForm
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        # 種別を登録
        form.instance.kind = EmailToken.KindChoices.EMAIL_UPDATE

        # 作成ユーザーを登録
        form.instance.created_user = self.request.user

        # Eメールトークンを作成
        form.instance.save()

        # Email を送信
        send_email(
            'Eメールアドレス変更の手続きを続行してください',
            form.instance.email,
            'home/mails/update_email_email.txt',
            {'token': form.instance},
        )

        # 成功メッセージを追加
        messages.warning(
            self.request,
            'Eメールアドレス変更用Eメールを送信しました。'
            'メールの指示に従い、手続きを続けてください。'
        )

        return super().form_valid(form)


class UpdateEmailView(auth_mixins.LoginRequiredMixin, generic.RedirectView):
    """Eメールアドレス変更
    """
    url = reverse_lazy('home:profile')

    def get(self, request, *args, **kwargs):
        # Eメールトークンを取得
        token = \
            get_object_or_404(EmailToken, id=kwargs.get('token_id'))

        # 有効性を判定
        if not token.validate(EmailToken.KindChoices.EMAIL_UPDATE):
            raise Http404

        with transaction.atomic():
            # Eメールアドレスを変更
            user = token.created_user
            user.email = token.email
            user.save()

            # トークンを無効化
            token.is_used = True
            token.save()

        # Email を送信
        send_email(
            'Eメールアドレスを変更しました',
            token.email,
            'home/mails/update_email.txt'
        )

        # メッセージを追加
        messages.success(request, 'Eメールアドレスを変更しました！')

        return super().get(request, *args, **kwargs)


class UpdateDisplayNameView(
        auth_mixins.LoginRequiredMixin, generic.UpdateView):
    """表示名変更
    """
    template_name = 'home/update_display_name.html'
    form_class = forms.UpdateDisplayNameForm
    model = get_user_model()
    success_url = reverse_lazy('home:profile')

    def get_object(self, queryset=None):
        # ログインしている自身の User についてのみ変更可能
        return self.request.user

    def form_valid(self, form):
        # 保存
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.warning(self.request, '表示名を変更しました！')

        return response


class UpdatePasswordView(auth_mixins.LoginRequiredMixin, generic.FormView):
    """パスワード変更
    """
    template_name = 'home/update_password.html'
    form_class = forms.UpdatePasswordForm
    success_url = reverse_lazy('home:profile')

    def form_valid(self, form):
        # ログイン中のユーザーを取得
        user = self.request.user

        # フォームの値を取得
        old_password = form.cleaned_data.get('old_password')
        new_password = form.cleaned_data.get('new_password')

        # 古いパスワードが一致していなかった場合は拒否
        if not self.request.user.check_password(old_password):
            form.add_error('old_password', ValidationError(
                '古いパスワードが誤っています。', code='invalid')
            )
            form.add_error('new_password', ValidationError(
                'もう一度入力してください。', code='invalid'
            ))
            return super().form_invalid(form)

        # 新しいパスワードが制約に適合しない場合は拒否
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            form.add_error('old_password', ValidationError(
                'もう一度入力してください。', code='invalid'
            ))
            form.add_error('new_password', e)
            return super().form_invalid(form)

        # 問題なければ新しいパスワードを設定
        user.set_password(new_password)
        user.save()

        # set_password() を実行するとログアウトしてしまうので
        # 自動的にログインさせる
        login(self.request, user)

        # 成功メッセージを追加
        messages.warning(self.request, 'パスワードを変更しました。')

        return super().form_valid(form)


class DeleteUserView(auth_mixins.LoginRequiredMixin, generic.FormView):
    """アカウント削除
    """
    template_name = 'home/delete_user.html'
    form_class = forms.DeleteUserForm
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        # ログイン中のユーザーを取得
        user = self.request.user

        # 削除する前にメールアドレスを取得
        email = user.email

        # ユーザーを削除
        user.delete()

        # Email を送信
        send_email(
            'アカウントを削除しました',
            email,
            'home/mails/delete_user.txt'
        )

        # 成功メッセージを追加
        messages.success(self.request, 'アカウントを削除しました。')

        return super().form_valid(form)


class ManageUsersView(
        auth_mixins.PermissionRequiredMixin, generic.TemplateView):
    """ユーザー管理
    """
    template_name = 'home/manage_users.html'
    permission_required = 'home.raildb_manage_users'
    raise_exception = True


class UpdateUserStaffView(
        auth_mixins.PermissionRequiredMixin, generic.UpdateView):
    """ユーザー編集（スタッフ専用）
    """
    template_name = 'home/update_user_staff.html'
    permission_required = 'home.raildb_manage_users'
    raise_exception = True
    pk_url_kwarg = 'user_id'
    model = get_user_model()
    form_class = forms.UpdateUserStaffForm

    def get_success_url(self):
        return reverse(
            'home:update_user_staff', kwargs={'user_id': self.object.id})

    def form_valid(self, form):
        # スタッフの場合は拒否
        if self.object.is_staff:
            messages.error(self.request, 'スタッフの情報は編集できません！')
            return super().form_invalid(form)

        # 成功メッセージを追加
        messages.success(self.request, f'{form.instance} さんのユーザー情報を編集しました！')

        return super().form_valid(form)


class DeleteUserStaffView(
        auth_mixins.PermissionRequiredMixin, generic.RedirectView):
    """ユーザー削除（スタッフ専用）
    """
    permission_required = 'home.raildb_manage_users'
    raise_exception = True
    url = reverse_lazy('home:manage_users')

    def get(self, request, *args, **kwargs):
        # URL からユーザーを取得
        user = get_object_or_404(get_user_model(), id=kwargs.get('user_id'))

        # スタッフのアカウントは削除不可
        if user.is_staff:
            messages.error(
                request,
                'スタッフは削除できません！'
            )
            return super().get(request, *args, **kwargs)

        # 削除
        user.delete()

        # メッセージを追加
        messages.success(
            request,
            f'ユーザー "{user}" を削除しました！'
        )

        return super().get(request, *args, **kwargs)


class ManagePermissionsView(
        auth_mixins.UserPassesTestMixin, generic.TemplateView):
    """ユーザー権限管理
    """
    template_name = 'home/manage_permissions.html'
    raise_exception = True

    def test_func(self):
        # システム管理者のみアクセス可能
        return self.request.user.is_authenticated \
            and self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_model = get_user_model()

        # スタッフ一覧
        context['staff_list'] = \
            user_model.objects.filter(is_staff=True)

        # グループ一覧
        context['group_list'] = Group.objects.all()

        return context


class RegisterStaffView(auth_mixins.UserPassesTestMixin, generic.FormView):
    """スタッフ権限付与
    """
    template_name = 'home/register_staff.html'
    form_class = forms.RegisterStaffForm
    success_url = reverse_lazy('home:manage_permissions')
    raise_exception = True

    def test_func(self):
        # システム管理者のみアクセス可能
        return self.request.user.is_authenticated \
            and self.request.user.is_superuser

    def form_valid(self, form):
        # 与えられた email の User にスタッフ権限を与える
        user_model = get_user_model()
        user = user_model.objects.get(email=form.cleaned_data.get('email'))
        user.is_staff = True
        user.save()

        # メッセージを追加
        messages.success(
            self.request,
            f'{user} さんがスタッフになりました。'
        )

        return super().form_valid(form)


class UnregisterStaffView(
        auth_mixins.UserPassesTestMixin, generic.RedirectView):
    """スタッフ解除
    """
    url = reverse_lazy('home:manage_permissions')
    raise_exception = True

    def test_func(self):
        # システム管理者のみアクセス可能
        return self.request.user.is_authenticated \
            and self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        # URL からユーザーを取得
        user = get_object_or_404(get_user_model(), id=kwargs.get('user_id'))

        # システム管理者の場合は操作不可
        if user.is_superuser:
            messages.error(
                request,
                'システム担当者の権限は解除できません！'
            )
            return super().get(request, *args, **kwargs)

        # スタッフ権限を剥奪
        user.is_staff = False
        user.save()

        # メッセージを追加
        messages.success(
            request,
            f'{user} のスタッフ権限を解除しました！'
        )

        return super().get(request, *args, **kwargs)


class CreateGroupView(auth_mixins.UserPassesTestMixin, generic.CreateView):
    """グループ作成
    """
    template_name = 'home/create_group.html'
    form_class = forms.GroupForm
    success_url = reverse_lazy('home:manage_permissions')
    raise_exception = True
    model = Group

    def test_func(self):
        # システム管理者のみアクセス可能
        return self.request.user.is_authenticated \
            and self.request.user.is_superuser

    def form_valid(self, form):
        with transaction.atomic():
            # Group を保存
            response = super().form_valid(form)

            # 権限
            self.object.permissions.set(
                form.cleaned_data.get('permissions')
            )

            # メンバーを追加
            for user in form.cleaned_data.get('user_list'):
                user.groups.add(self.object)
                user.save()

        messages.success(
            self.request,
            f'グループ "{self.object}" を作成しました！'
        )

        return response


class UpdateGroupView(auth_mixins.UserPassesTestMixin, generic.UpdateView):
    """グループ編集
    """
    template_name = 'home/update_group.html'
    form_class = forms.GroupForm
    success_url = reverse_lazy('home:manage_permissions')
    raise_exception = True
    model = Group
    pk_url_kwarg = 'group_id'

    def test_func(self):
        # システム管理者のみアクセス可能
        return self.request.user.is_authenticated \
            and self.request.user.is_superuser

    def get_initial(self):
        initial = super().get_initial()

        initial.update({
            'permissions': self.object.permissions.all(),
            'user_list': self.object.user_set.all()
        })

        return initial

    def form_valid(self, form):
        with transaction.atomic():
            # Group を保存
            response = super().form_valid(form)

            # 権限
            self.object.permissions.set(
                form.cleaned_data.get('permissions')
            )

            # 一旦メンバーを全解除
            for user in self.object.user_set.all():
                user.groups.remove(self.object)

            # メンバーを追加
            for user in form.cleaned_data.get('user_list'):
                user.groups.add(self.object)
                user.save()

        messages.success(
            self.request,
            f'グループ "{self.object}" を編集しました！'
        )

        return response


class DeleteGroupView(auth_mixins.UserPassesTestMixin, generic.RedirectView):
    """グループ削除
    """
    url = reverse_lazy('home:manage_permissions')
    raise_exception = True

    def test_func(self):
        # システム管理者のみアクセス可能
        return self.request.user.is_authenticated \
            and self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        # URL からグループを取得
        group = get_object_or_404(Group, id=kwargs.get('group_id'))

        # 削除
        group.delete()

        # メッセージを追加
        messages.success(
            request,
            f'グループ "{group}" を削除しました！'
        )

        return super().get(request, *args, **kwargs)


class NewsListView(auth_mixins.PermissionRequiredMixin, generic.ListView):
    """お知らせ管理
    """
    permission_required = 'home.raildb_manage_news'
    template_name = 'news_list.html'
    model = News


class NewsCreateView(auth_mixins.PermissionRequiredMixin, generic.CreateView):
    """お知らせ作成
    """
    permission_required = 'home.raildb_manage_news'
    template_name = 'home/news_create.html'
    model = News
    fields = ['kind', 'title', 'body']
    success_url = reverse_lazy('home:news_list')

    def form_valid(self, form):
        # 作成
        response = super().form_valid(form)

        # 最終更新者を登録
        self.object.update_user = self.request.user
        self.object.save()

        # メッセージを追加
        messages.success(
            self.request,
            f'メッセージ "{self.object.title}" を追加しました！'
        )

        return response


class NewsUpdateView(auth_mixins.PermissionRequiredMixin, generic.UpdateView):
    """お知らせ編集
    """
    permission_required = 'home.raildb_manage_news'
    template_name = 'home/news_update.html'
    model = News
    fields = ['kind', 'title', 'body']

    def get_success_url(self):
        return reverse(
            'home:news_update', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        # 更新
        response = super().form_valid(form)

        # 最終更新者を登録
        self.object.update_user = self.request.user
        self.object.save()

        # メッセージを追加
        messages.success(
            self.request,
            f'メッセージ "{self.object.title}" を編集しました！'
        )

        return response


class NewsDeleteView(auth_mixins.PermissionRequiredMixin, generic.DeleteView):
    """お知らせ削除
    """
    permission_required = 'home.raildb_manage_news'
    template_name = 'home/news_delete.html'
    model = News
    success_url = reverse_lazy('home:news_list')

    def form_valid(self, form):
        # 削除
        response = super().form_valid(form)

        # メッセージを追加
        messages.success(
            self.request,
            f'メッセージ "{self.object.title}" を削除しました！'
        )

        return response


class NewsDetailView(generic.DetailView):
    """お知らせ詳細
    """
    template_name = 'home/news_detail.html'
    model = News


# JSON


class JsonUser(
        auth_mixins.PermissionRequiredMixin, BaseDatatableView):
    """JSON: ユーザー管理
    """
    permission_required = 'home.raildb_manage_users'
    raise_exception = True
    model = get_user_model()
    columns = [
        'email', 'display_name', 'is_active', 'is_staff', 'is_superuser', 'id'
    ]
    max_display_length = 500
