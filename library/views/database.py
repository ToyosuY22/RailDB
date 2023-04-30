import csv
import io
import traceback

from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic

from library import forms
from library.models import Line, Operator, Station
from raildb.mixins import SuperUserOnlyMixin


class SearchOperatorView(generic.TemplateView):
    template_name = 'library/database/search_operator.html'


class SearchLineView(generic.TemplateView):
    template_name = 'library/database/search_line.html'


class SearchStationView(generic.TemplateView):
    template_name = 'library/database/search_station.html'


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
            'gap': self.get_gap(station)
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


class CsvDownloadView(generic.View):
    """CSVダウンロード
    """
    # 想定されている mode の一覧（URL から取得）
    expected_mode_list = ['operator', 'line', 'station']

    def get(self, request, *args, **kwargs):
        # mode を URL から取得
        # ただし想定されていない mode が与えられた場合は 404
        given_mode = kwargs.get('mode')
        if given_mode in self.expected_mode_list:
            mode = given_mode
        else:
            raise Http404

        # instance を URL から取得（ある場合のみ）
        # e.g., 事業者の pk が与えられた場合は、その事業者に属する路線のみを取得
        if 'pk' in kwargs:
            instance = self.get_instance(mode, kwargs['pk'])
        else:
            instance = None

        # ファイル名を取得
        filename = self.get_filename(mode, instance)

        # HTTP ヘッダーを設定
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            },
        )

        # CSV 書込み開始
        writer = csv.writer(response)

        # CSV ヘッダー行書込み
        header = self.get_header(mode)
        writer.writerow(header)

        # queryset を取得
        queryset = self.get_queryset(mode, instance)

        # CSV 本文書込み
        for obj in queryset:
            row = self.get_body(mode, obj)
            writer.writerow(row)

        return response

    def get_filename(self, mode, instance):
        if instance:
            return f'{mode}_{instance.order}.csv'
        else:
            return f'{mode}.csv'

    def get_instance(self, mode, pk):
        # 事業者の場合は無視
        if mode == 'line':
            return get_object_or_404(Operator, id=pk)
        elif mode == 'station':
            return get_object_or_404(Line, id=pk)

    def get_header(self, mode):
        if mode == 'operator':
            return [
                'name', 'name_kana'
            ]
        elif mode == 'line':
            return [
                'name', 'name_kana',
                'start', 'end', 'via', 'area', 'kind', 'status',
                'category', 'distance', 'note'
            ]
        elif mode == 'station':
            return [
                'name', 'name_kana',
                'distance', 'label', 'freight', 'note'
            ]

    def get_queryset(self, mode, instance):
        if mode == 'operator':
            # 事業者の場合は instance を指定しても無視
            return Operator.objects.all()
        elif mode == 'line':
            if instance:
                return Line.objects.filter(operator=instance)
            else:
                return Line.objects.all()
        elif mode == 'station':
            if instance:
                return Station.objects.filter(line=instance)
            else:
                return Station.objects.all()

    def get_body(self, mode, obj):
        if mode == 'operator':
            return [
                obj.name,
                obj.name_kana
            ]
        elif mode == 'line':
            return [
                obj.name,
                obj.name_kana,
                obj.start,
                obj.end,
                obj.via,
                obj.area,
                obj.kind,
                obj.status,
                obj.category,
                obj.distance,
                obj.note
            ]
        elif mode == 'station':
            return [
                obj.name,
                obj.name_kana,
                obj.distance,
                obj.label,
                obj.freight,
                obj.note
            ]


class CsvUploadView(SuperUserOnlyMixin, generic.FormView):
    """CSVアップロード
    """
    template_name = 'library/database/csv_upload.html'
    form_class = forms.UploadForm

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
        # 路線の id を URL パラメータとして付与
        return reverse(
            'library:database_detail_line', kwargs={'pk': self.line.id}
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        # CSV 読み込み
        data = io.TextIOWrapper(
            self.request.FILES.get('file'), encoding='utf-8'
        )
        reader = csv.reader(data)

        # ヘッダー行を捨てる
        _ = next(csv.reader(data))

        try:
            with transaction.atomic():
                # 一旦すべての所属駅を削除
                Station.objects.filter(line=self.line).delete()

                # CSV データを元に液を作製
                for row in reader:
                    Station.objects.create(
                        name=row[0],
                        name_kana=row[1],
                        line=self.line,
                        distance=int(row[2]),
                        label=row[3] if row[3] else None,
                        note=row[4]
                    )
        except Exception as e:
            # エラー内容を表示
            message = traceback.format_exc()
            form.add_error('file', e)
            form.add_error('file', message)
            return super().form_invalid(form)

        # メッセージを追加
        messages.success(self.request, '処理完了しました！')

        return response
