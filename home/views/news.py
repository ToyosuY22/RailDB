"""お知らせ管理

権限 home.raildb_manage_news が必要
"""

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views import generic
from home.models import News


class ListView(PermissionRequiredMixin, generic.ListView):
    """お知らせ管理
    """
    permission_required = 'home.raildb_manage_news'
    raise_exception = True
    template_name = 'home/news/list.html'
    model = News


class DetailView(generic.DetailView):
    """お知らせ詳細

    この View のみ home.raildb_manage_news は不要
    """
    template_name = 'home/news/detail.html'
    model = News


class CreateView(PermissionRequiredMixin, generic.CreateView):
    """お知らせ作成
    """
    permission_required = 'home.raildb_manage_news'
    raise_exception = True
    template_name = 'home/news/create.html'
    model = News
    fields = ['kind', 'title', 'body']
    success_url = reverse_lazy('home:news_list')

    def form_valid(self, form):
        # 最終更新者を登録
        form.instance.update_user = self.request.user

        # 作成
        response = super().form_valid(form)

        # メッセージを追加
        messages.success(
            self.request,
            f'メッセージ "{self.object.title}" を追加しました！'
        )

        return response


class UpdateView(PermissionRequiredMixin, generic.UpdateView):
    """お知らせ編集
    """
    permission_required = 'home.raildb_manage_news'
    raise_exception = True
    template_name = 'home/news/update.html'
    model = News
    fields = ['kind', 'title', 'body']

    def get_success_url(self):
        return reverse(
            'home:news_update', kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        # 最終更新者を登録
        form.instance.update_user = self.request.user

        # 更新
        response = super().form_valid(form)

        # メッセージを追加
        messages.success(
            self.request,
            f'メッセージ "{self.object.title}" を編集しました！'
        )

        return response


class DeleteView(PermissionRequiredMixin, generic.DeleteView):
    """お知らせ削除
    """
    permission_required = 'home.raildb_manage_news'
    raise_exception = True
    template_name = 'home/news/delete.html'
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
