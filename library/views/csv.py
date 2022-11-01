import csv
import io
import traceback
import uuid

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404, HttpResponse
from django.urls import reverse
from django.views import generic
from library import forms
from library.models import Line, Operator, Station
from raildb.mixins import SuperUserOnlyMixin


class UploadView(SuperUserOnlyMixin, generic.FormView):
    """CSVアップロード
    """
    template_name = 'library/csv/upload.html'
    form_class = forms.UploadForm

    # 想定されている mode の一覧（URL から取得）
    expected_mode_list = ['operator', 'line', 'station']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        # mode を URL から取得
        # ただし想定されていない mode が与えられた場合は 404
        given_mode = kwargs.get('mode')
        if given_mode in self.expected_mode_list:
            self.mode = given_mode
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # モード
        context['mode'] = self.mode
        return context

    def get_success_url(self):
        return reverse(
            'library:csv_upload', kwargs={'mode': self.mode}
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
                for row in reader:
                    if row[0] == 'add':
                        self.add_data(row)
                    elif row[0] == 'download':
                        # 何もしない
                        continue
                    else:
                        # command 不正
                        raise ValidationError(
                            f'command が不正です：{row[0]}',
                            code='command'
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

    def add_data(self, row):
        if self.mode == 'operator':
            # 事業者
            Operator.objects.create(
                id=uuid.UUID(row[1]),
                name=row[2],
                name_kana=row[3]
            )
        elif self.mode == 'line':
            # 路線
            operator = Operator.objects.get(id=uuid.UUID(row[4]))
            Line.objects.create(
                id=row[1],
                name=row[2],
                name_kana=row[3],
                operator=operator,
                start=row[5],
                end=row[6],
                via=row[7],
                area=row[8],
                kind=row[9],
                status=row[10],
                category=row[11],
                distance=row[12],
                note=row[13]
            )
        elif self.mode == 'station':
            # 駅
            line = Line.objects.get(id=uuid.UUID(row[4]))
            Station.objects.create(
                id=row[1],
                name=row[2],
                name_kana=row[3],
                line=line,
                distance=row[5] if row[5] else None,
                label=row[6],
                note=row[7]
            )


class DownloadView(generic.View):
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

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{mode}.csv"'
            },
        )

        writer = csv.writer(response)

        if mode == 'operator':
            # header
            writer.writerow([
                'command',
                'id',
                'name',
                'name_kana'
            ])
            # body
            for operator in Operator.objects.all():
                writer.writerow([
                    'download',
                    operator.id,
                    operator.name,
                    operator.name_kana
                ])
        elif mode == 'line':
            # header
            writer.writerow([
                'command',
                'id',
                'name',
                'name_kana',
                'operator_id',
                'start',
                'end',
                'via',
                'area',
                'kind',
                'status',
                'category',
                'distance',
                'note'
            ])
            # body
            for line in Line.objects.all():
                writer.writerow([
                    'download',
                    line.id,
                    line.name,
                    line.name_kana,
                    line.operator.id,
                    line.start,
                    line.end,
                    line.via,
                    line.area,
                    line.kind,
                    line.status,
                    line.category,
                    line.distance,
                    line.note
                ])
        elif mode == 'station':
            # header
            writer.writerow([
                'command',
                'id',
                'name',
                'name_kana',
                'line_id',
                'distance',
                'label',
                'note'
            ])
            # body
            for station in Station.objects.all():
                writer.writerow([
                    'download',
                    station.id,
                    station.name,
                    station.name_kana,
                    station.line.id,
                    station.distance,
                    station.label,
                    station.note
                ])

        return response
