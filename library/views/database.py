from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic

from library import forms
from library.models import Line, LineRelationship, Operator, Station
from raildb.mixins import SuperUserOnlyMixin


class SearchOperatorView(generic.TemplateView):
    template_name = 'library/database/search_operator.html'


class SearchLineView(generic.TemplateView):
    template_name = 'library/database/search_line.html'


class SearchStationView(generic.TemplateView):
    template_name = 'library/database/search_station.html'


class ListLineRelationshipView(SuperUserOnlyMixin, generic.TemplateView):
    template_name = 'library/database/list_line_relationship.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        object_list = []

        # 路線関係データを登録
        for line_relationship in LineRelationship.objects.all():
            object_list.append({
                'line_relationship': line_relationship,
                'distance': {
                    'transport':
                        line_relationship.transport_end.distance
                        - line_relationship.transport_start.distance,
                    'maintenance':
                        line_relationship.maintenance_end.distance
                        - line_relationship.maintenance_start.distance,
                }
            })

        context['object_list'] = object_list

        return context


class DetailOperatorView(generic.DetailView):
    template_name = 'library/database/detail_operator.html'
    model = Operator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 事業者の情報を取得
        operator = self.object

        # 初期化
        line_list = []

        # 種別／状態／事業ごとに集計
        for kind in Line.KindChoices:
            for status in Line.StatusChoices:
                for category in Line.CategoryChoices:
                    # 路線一覧を取得
                    line_queryset = Line.objects.filter(
                        operator=operator,
                        kind=kind,
                        status=status,
                        category=category
                    )

                    # 該当件数が 1 件以上であれば追加
                    if line_queryset.exists():
                        line_list.append({
                            'kind': kind,
                            'status': status,
                            'category': category,
                            'queryset': line_queryset,
                            'distance_sum': line_queryset.aggregate(
                                Sum('distance'))['distance__sum']
                        })

        # 路線一覧を登録
        context['line_list'] = line_list

        return context


class DetailLineView(generic.DetailView):
    template_name = 'library/database/detail_line.html'
    model = Line

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 駅一覧を登録
        context['object_list'] = [{
            'station': station,
            'gap': self.get_gap(station),
        } for station in Station.objects.filter(line=self.object)]

        return context

    def get_gap(self, this_station):
        # 区間キロ程を求める
        # キロ程が登録されていて、かつ自駅より前の駅を抽出
        station_list = Station.objects.filter(
            line=self.object,
            distance__isnull=False,
            order__lt=this_station.order
        )

        # 該当する駅が空の場合は値なし
        if not station_list:
            return None

        previous_station = station_list.last()

        try:
            return this_station.distance - previous_station.distance
        except TypeError:
            # キロ程 None
            return None


class DetailStationView(generic.DetailView):
    template_name = 'library/database/detail_station.html'
    model = Station


class CreateOperatorView(SuperUserOnlyMixin, generic.CreateView):
    template_name = 'library/database/create_operator.html'
    model = Operator
    form_class = forms.OperatorForm

    def get_success_url(self):
        # 作成したモデルの id を URL パラメータとして付与
        return reverse(
            'library:database_order_operator', kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        # 作成
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'事業者 {self.object} を作成しました！続いて順序を指定してください'
        )

        return response


class OrderOperatorView(SuperUserOnlyMixin, generic.FormView):
    template_name = 'library/database/order_operator.html'
    form_class = forms.OrderForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        # object を URL から取得
        # ただし想定されていない pk が与えられた場合は 404
        given_pk = kwargs.get('pk')
        self.object = get_object_or_404(Operator, pk=given_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URL で指定した事業者
        context['object'] = self.object
        # 事業者一覧
        context['object_list'] = Operator.objects.all()

        return context

    def get_success_url(self):
        # 作成したモデルの id を URL パラメータとして付与
        return reverse(
            'library:database_detail_operator', kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        # フォームから値を取得
        given_order = form.cleaned_data.get('order')
        # 順序を設定
        self.object.to(given_order)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'事業者 {self.object} の順序を {self.object.order} に設定しました！'
        )

        return response


class UpdateOperatorView(SuperUserOnlyMixin, generic.UpdateView):
    template_name = 'library/database/update_operator.html'
    model = Operator
    form_class = forms.OperatorForm

    def get_success_url(self):
        # 作成したモデルの id を URL パラメータとして付与
        return reverse(
            'library:database_detail_operator', kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        # 編集
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'事業者 {self.object} を編集しました！'
        )

        return response


class DeleteOperatorView(SuperUserOnlyMixin, generic.DeleteView):
    template_name = 'library/database/delete_operator.html'
    model = Operator
    success_url = reverse_lazy('library:database_search_operator')

    def form_valid(self, form):
        # 削除
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'事業者 {self.object} を削除しました！'
        )

        return response


class CreateLineView(SuperUserOnlyMixin, generic.CreateView):
    template_name = 'library/database/create_line.html'
    model = Line
    form_class = forms.LineForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        # 路線が所属する事業者を URL から取得
        # ただし想定されていない pk が与えられた場合は 404
        given_pk = kwargs.get('operator_pk')
        self.operator = get_object_or_404(Operator, pk=given_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URL で指定した事業者
        context['operator'] = self.operator

        return context

    def get_success_url(self):
        # 作成したモデルの id を URL パラメータとして付与
        return reverse(
            'library:database_order_line', kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        # 路線を登録
        form.instance.operator = self.operator
        # 作成
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'路線 {self.object} を作成しました！続いて順序を指定してください'
        )

        return response


class OrderLineView(SuperUserOnlyMixin, generic.FormView):
    template_name = 'library/database/order_line.html'
    form_class = forms.OrderForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        # object を URL から取得
        # ただし想定されていない pk が与えられた場合は 404
        given_pk = kwargs.get('pk')
        self.object = get_object_or_404(Line, pk=given_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URL で指定した路線
        context['object'] = self.object
        # 路線一覧
        context['object_list'] = Line.objects.all()

        return context

    def get_success_url(self):
        # 作成したモデルの id を URL パラメータとして付与
        return reverse(
            'library:database_detail_line', kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        # フォームから値を取得
        given_order = form.cleaned_data.get('order')
        # 順序を設定
        self.object.to(given_order)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'路線 {self.object} の順序を {self.object.order} に設定しました！'
        )

        return response


class UpdateLineView(SuperUserOnlyMixin, generic.UpdateView):
    template_name = 'library/database/update_line.html'
    model = Line
    form_class = forms.LineForm

    def get_success_url(self):
        # 作成したモデルの id を URL パラメータとして付与
        return reverse(
            'library:database_detail_line', kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        # 編集
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'路線 {self.object} を編集しました！'
        )

        return response


class UpdateLineOperatorView(SuperUserOnlyMixin, generic.UpdateView):
    template_name = 'library/database/update_line_operator.html'
    model = Line
    form_class = forms.LineOperatorForm

    def get_success_url(self):
        # 変更したモデルの id を URL パラメータとして付与
        return reverse(
            'library:database_detail_line', kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        # 編集
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'路線 {self.object} の事業者を {self.object.operator} に変更しました！'
        )

        return response


class DeleteLineView(SuperUserOnlyMixin, generic.DeleteView):
    template_name = 'library/database/delete_line.html'
    model = Line

    def get_success_url(self):
        # 事業者の詳細ページに戻す
        return reverse(
            'library:database_detail_operator',
            kwargs={'pk': self.object.operator.id}
        )

    def form_valid(self, form):
        # 削除
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'路線 {self.object} を削除しました！'
        )

        return response


class CreateStationView(SuperUserOnlyMixin, generic.CreateView):
    template_name = 'library/database/create_station.html'
    model = Station
    form_class = forms.StationForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        # 駅が所属する路線を URL から取得
        # ただし想定されていない pk が与えられた場合は 404
        given_pk = kwargs.get('line_pk')
        self.line = get_object_or_404(Line, pk=given_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URL で指定した事業者
        context['line'] = self.line

        return context

    def get_success_url(self):
        # 作成したモデルの id を URL パラメータとして付与
        return reverse(
            'library:database_order_station', kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        # 路線を登録
        form.instance.line = self.line
        # 作成
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'駅 {self.object} を作成しました！続いて順序を指定してください'
        )

        return response


class OrderStationView(SuperUserOnlyMixin, generic.FormView):
    template_name = 'library/database/order_station.html'
    form_class = forms.OrderForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        # object を URL から取得
        # ただし想定されていない pk が与えられた場合は 404
        given_pk = kwargs.get('pk')
        self.object = get_object_or_404(Station, pk=given_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URL で指定した駅
        context['object'] = self.object
        # 同一路線に所属する駅一覧
        context['object_list'] = Station.objects.filter(
            line=self.object.line
        )

        return context

    def get_success_url(self):
        # 作成したモデルの id を URL パラメータとして付与
        return reverse(
            'library:database_detail_station', kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        # フォームから値を取得
        given_order = form.cleaned_data.get('order')
        # 順序を設定
        self.object.to(given_order)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'駅 {self.object} の順序を {self.object.order} に設定しました！'
        )

        return response


class UpdateStationView(SuperUserOnlyMixin, generic.UpdateView):
    template_name = 'library/database/update_station.html'
    model = Station
    form_class = forms.StationForm

    def get_success_url(self):
        # 作成したモデルの id を URL パラメータとして付与
        return reverse(
            'library:database_detail_station', kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        # 編集
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'駅 {self.object} を編集しました！'
        )

        return response


class UpdateStationLineView(SuperUserOnlyMixin, generic.UpdateView):
    template_name = 'library/database/update_station_line.html'
    model = Station
    form_class = forms.StationLineForm

    def get_success_url(self):
        # 変更したモデルの id を URL パラメータとして付与
        return reverse(
            'library:database_detail_station', kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        # 編集
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'駅 {self.object} の路線を {self.object.line} に変更しました！'
        )

        return response


class DeleteStationView(SuperUserOnlyMixin, generic.DeleteView):
    template_name = 'library/database/delete_station.html'
    model = Station

    def get_success_url(self):
        # 路線の詳細ページに戻す
        return reverse(
            'library:database_detail_line',
            kwargs={'pk': self.object.line.id}
        )

    def form_valid(self, form):
        # 削除
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'駅 {self.object} を削除しました！'
        )

        return response


def set_queryset_line_relationship(form):
    """LineRelationship の selec2 form において使用する queryset を設定する
    """
    # 運送路線
    line_list_transport = Station.objects.filter(
        line__category__in=['train_2', 'tram_transport']
    )
    # 整備路線
    line_list_maintenance = Station.objects.filter(
        line__category__in=['train_1', 'train_3', 'tram_maintenance']
    )
    # queryset を指定
    form.fields['transport_start'].queryset = line_list_transport
    form.fields['transport_end'].queryset = line_list_transport
    form.fields['maintenance_start'].queryset = line_list_maintenance
    form.fields['maintenance_end'].queryset = line_list_maintenance

    return form


class CreateLineRelationshipView(SuperUserOnlyMixin, generic.CreateView):
    template_name = 'library/database/create_line_relationship.html'
    model = LineRelationship
    form_class = forms.LineRelationshipForm
    success_url = reverse_lazy('library:database_list_line_relationship')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return set_queryset_line_relationship(form)

    def form_valid(self, form):
        # 作成
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'路線関係 {self.object} を作成しました！'
        )

        return response


class UpdateLineRelationshipView(SuperUserOnlyMixin, generic.UpdateView):
    template_name = 'library/database/update_line_relationship.html'
    model = LineRelationship
    form_class = forms.LineRelationshipForm
    success_url = reverse_lazy('library:database_list_line_relationship')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return set_queryset_line_relationship(form)

    def form_valid(self, form):
        # 作成
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'路線関係 {self.object} を編集しました！'
        )

        return response


class DeleteLineRelationshipView(SuperUserOnlyMixin, generic.DeleteView):
    model = LineRelationship
    success_url = reverse_lazy('library:database_list_line_relationship')

    def form_valid(self, form):
        # 削除
        response = super().form_valid(form)

        # 成功メッセージを追加
        messages.success(
            self.request,
            f'路線関係 {self.object} を削除しました！'
        )

        return response
