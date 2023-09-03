import csv
import zipfile
from io import StringIO

import pykakasi
from django.db.models import Sum
from django.http import HttpResponse
from django.views import generic
from import_export.resources import ModelResource

from ekidata import models as ekidata_models
from library.models import Line, Operator, Station
from raildb.mixins import SuperUserOnlyMixin


class AreaView(generic.TemplateView):
    template_name = 'library/summary/area.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 運輸局別鉄道／軌道営業キロ一覧表
        context['area_object'] = self.get_area_object()
        return context

    def get_area_object(self):
        # 運輸局別鉄道／軌道営業キロ一覧表
        # 配列を初期化
        result = []

        # 運輸局ごとに集計
        for area in Line.AreaChoices:
            # JR, その他は除外
            if area in [Line.AreaChoices.JR, Line.AreaChoices.OTHER]:
                continue

            # まずは運輸局で制限（開業線のみ）
            line_queryset = Line.objects.filter(
                area=area,
                status=Line.StatusChoices.ACTIVE
            )

            # 第1種鉄道／第2種鉄道
            line_queryset_train_transport = line_queryset.filter(
                category__in=[
                    Line.CategoryChoices.TRAIN_1,
                    Line.CategoryChoices.TRAIN_2
                ]
            )

            # 第3種鉄道
            line_queryset_train_maintenance = line_queryset.filter(
                category=Line.CategoryChoices.TRAIN_3
            )

            # 軌道運送
            line_queryset_tram_transport = line_queryset.filter(
                category=Line.CategoryChoices.TRAM_TRANSPORT
            )

            # 軌道整備
            line_queryset_tram_maintenance = line_queryset.filter(
                category=Line.CategoryChoices.TRAM_MAINTENANCE
            )

            # 集計／鉄道／開業者数
            summary_train_operator = line_queryset.filter(
                category__in=[
                    Line.CategoryChoices.TRAIN_1,
                    Line.CategoryChoices.TRAIN_2,
                    Line.CategoryChoices.TRAIN_3,
                ]
            ).values('operator_id').distinct().count()

            # 集計／鉄道／開業者数（整備内数）
            summary_train_operator_maintenance = line_queryset.filter(
                category=Line.CategoryChoices.TRAIN_3
            ).values('operator_id').distinct().count()

            # 集計／鉄道／キロ程
            summary_train_distance = line_queryset.filter(
                category__in=[
                    Line.CategoryChoices.TRAIN_1,
                    Line.CategoryChoices.TRAIN_2
                ]
            ).aggregate(Sum('distance'))['distance__sum']

            # 集計／軌道／開業者数
            summary_tram_operator = line_queryset.filter(
                category__in=[
                    Line.CategoryChoices.TRAM_TRANSPORT,
                    Line.CategoryChoices.TRAM_MAINTENANCE
                ]
            ).values('operator_id').distinct().count()

            # 集計／軌道／開業者数（整備内数）
            summary_tram_operator_maintenance = line_queryset.filter(
                category=Line.CategoryChoices.TRAM_MAINTENANCE
            ).values('operator_id').distinct().count()

            # 集計／軌道／キロ程
            summary_tram_distance = line_queryset.filter(
                category=Line.CategoryChoices.TRAM_TRANSPORT
            ).aggregate(Sum('distance'))['distance__sum']

            # 集計／合計／開業者数
            summary_operator = \
                (summary_train_operator if summary_train_operator else 0) \
                + (summary_tram_operator if summary_tram_operator else 0)

            # 集計／合計／開業者数（整備内数）
            summary_operator_maintenance = \
                (summary_train_operator_maintenance
                    if summary_train_operator_maintenance else 0) \
                + (summary_tram_operator_maintenance
                    if summary_tram_operator_maintenance else 0)

            # 集計／合計／キロ程
            summary_distance = \
                (summary_train_distance if summary_train_distance else 0) \
                + (summary_tram_distance if summary_tram_distance else 0)

            result.append({
                'area': area,
                'train_transport':
                    self.group_by_operator(line_queryset_train_transport),
                'train_maintenance':
                    self.group_by_operator(line_queryset_train_maintenance),
                'tram_transport':
                    self.group_by_operator(line_queryset_tram_transport),
                'tram_maintenance':
                    self.group_by_operator(line_queryset_tram_maintenance),
                'summary_train_operator': summary_train_operator,
                'summary_train_operator_maintenance':
                    summary_train_operator_maintenance,
                'summary_train_distance': summary_train_distance,
                'summary_tram_operator': summary_tram_operator,
                'summary_tram_operator_maintenance':
                    summary_tram_operator_maintenance,
                'summary_tram_distance': summary_tram_distance,
                'summary_operator': summary_operator,
                'summary_operator_maintenance':
                    summary_operator_maintenance,
                'summary_distance': summary_distance
            })

        # エリア横断集計／鉄道／開業者数
        summary_train_operator = sum([
            data['summary_train_operator'] for data in result
            if data['summary_train_operator']
        ])

        # エリア横断集計／鉄道／開業者数（整備内数）
        summary_train_operator_maintenance = sum([
            data['summary_train_operator_maintenance'] for data in result
            if data['summary_train_operator_maintenance']
        ])

        # エリア横断集計／鉄道／キロ程
        summary_train_distance = sum([
            data['summary_train_distance'] for data in result
            if data['summary_train_distance']
        ])

        # エリア横断集計／軌道／開業者数
        summary_tram_operator = sum([
            data['summary_tram_operator'] for data in result
            if data['summary_tram_operator']
        ])

        # エリア横断集計／軌道／開業者数（整備内数）
        summary_tram_operator_maintenance = sum([
            data['summary_tram_operator_maintenance'] for data in result
            if data['summary_tram_operator_maintenance']
        ])

        # エリア横断集計／軌道／キロ程
        summary_tram_distance = sum([
            data['summary_tram_distance'] for data in result
            if data['summary_tram_distance']
        ])

        # エリア横断集計／合計／開業者数
        summary_operator = \
            (summary_train_operator if summary_train_operator else 0) \
            + (summary_tram_operator if summary_tram_operator else 0)

        # エリア横断集計／合計／開業者数（整備内数）
        summary_operator_maintenance = \
            (summary_train_operator_maintenance
                if summary_train_operator_maintenance else 0) \
            + (summary_tram_operator_maintenance
                if summary_tram_operator_maintenance else 0)

        # エリア横断集計／合計／キロ程
        summary_distance = \
            (summary_train_distance if summary_train_distance else 0) \
            + (summary_tram_distance if summary_tram_distance else 0)

        result.append({
            'area': 'sum',
            'summary_train_operator': summary_train_operator,
            'summary_train_operator_maintenance':
                summary_train_operator_maintenance,
            'summary_train_distance': summary_train_distance,
            'summary_tram_operator': summary_tram_operator,
            'summary_tram_operator_maintenance':
                summary_tram_operator_maintenance,
            'summary_tram_distance': summary_tram_distance,
            'summary_operator': summary_operator,
            'summary_operator_maintenance':
                summary_operator_maintenance,
            'summary_distance': summary_distance
        })

        return result

    def group_by_operator(self, queryset):
        # 事業者ごとに GROUP BY してキロ程を集計
        data = queryset.values('operator_id')\
            .annotate(distance_sum=Sum('distance'))\
            .values('operator_id', 'distance_sum')

        # 事業者をオブジェクトに変換
        return [{
            'operator': Operator.objects.get(id=row['operator_id']),
            'distance': row['distance_sum']
        } for row in data]


class KindView(generic.TemplateView):
    template_name = 'library/summary/kind.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 運輸局別鉄道／軌道営業キロ一覧表
        context['kind_object'] = self.get_kind_object()
        return context

    def get_kind_object(self):
        # 種別別鉄道／軌道営業キロ一覧表
        # 配列を初期化
        result = []

        # 運輸局ごとに集計
        for kind in Line.KindChoices:
            # その他は除外
            if kind == Line.KindChoices.OTHER:
                continue

            # 配列を初期化
            result_kind = []

            # 路線一覧を取得
            line_queryset = Line.objects.filter(kind=kind)

            if 'train' in kind.value:
                # 鉄道
                # 開業線／第1種
                active_train_1 = line_queryset.filter(
                    status=Line.StatusChoices.ACTIVE,
                    category=Line.CategoryChoices.TRAIN_1
                )
                active_train_1_summary = self.get_summary(active_train_1)
                result_kind.append({
                    'status': '開業線',
                    'category': '第1種',
                    'operator': active_train_1_summary['operator'],
                    'distance': active_train_1_summary['distance']
                })

                # 開業線／第2種
                active_train_2 = line_queryset.filter(
                    status=Line.StatusChoices.ACTIVE,
                    category__in=[
                        Line.CategoryChoices.TRAIN_2,
                        Line.CategoryChoices.TRAIN_2F
                    ]
                )
                active_train_2_summary = self.get_summary(active_train_2)
                result_kind.append({
                    'status': '開業線',
                    'category': '第2種',
                    'operator': active_train_2_summary['operator'],
                    'distance': active_train_2_summary['distance']
                })

                # 未開業線／第1種
                unopened_train_1 = line_queryset.filter(
                    status=Line.StatusChoices.UNOPENED,
                    category=Line.CategoryChoices.TRAIN_1
                )
                unopened_train_1_summary = self.get_summary(unopened_train_1)
                result_kind.append({
                    'status': '未開業線',
                    'category': '第1種',
                    'operator': unopened_train_1_summary['operator'],
                    'distance': unopened_train_1_summary['distance']
                })

                # 未開業線／第2種
                unopened_train_2 = line_queryset.filter(
                    status=Line.StatusChoices.UNOPENED,
                    category__in=[
                        Line.CategoryChoices.TRAIN_2,
                        Line.CategoryChoices.TRAIN_2F
                    ]
                )
                unopened_train_2_summary = self.get_summary(unopened_train_2)
                result_kind.append({
                    'status': '未開業線',
                    'category': '第2種',
                    'operator': unopened_train_2_summary['operator'],
                    'distance': unopened_train_2_summary['distance']
                })

                # 計／第1種
                train_1 = line_queryset.filter(
                    category=Line.CategoryChoices.TRAIN_1
                )
                train_1_summary = self.get_summary(train_1)
                result_kind.append({
                    'status': '計',
                    'category': '第1種',
                    'operator': train_1_summary['operator'],
                    'distance': train_1_summary['distance']
                })

                # 計／第2種
                train_2 = line_queryset.filter(
                    category__in=[
                        Line.CategoryChoices.TRAIN_2,
                        Line.CategoryChoices.TRAIN_2F
                    ]
                )
                train_2_summary = self.get_summary(train_2)
                result_kind.append({
                    'status': '計',
                    'category': '第2種',
                    'operator': train_2_summary['operator'],
                    'distance': train_2_summary['distance']
                })

            elif 'tram' in kind.value:
                # 軌道
                # 開業線
                active_tram = line_queryset.filter(
                    status=Line.StatusChoices.ACTIVE,
                    category=Line.CategoryChoices.TRAM_TRANSPORT
                )
                active_tram_summary = self.get_summary(active_tram)
                result_kind.append({
                    'status': '開業線',
                    'category': '軌道運送',
                    'operator': active_tram_summary['operator'],
                    'distance': active_tram_summary['distance']
                })

                # 未開業線
                unopened_tram = line_queryset.filter(
                    status=Line.StatusChoices.UNOPENED,
                    category=Line.CategoryChoices.TRAM_TRANSPORT
                )
                unopened_tram_summary = self.get_summary(unopened_tram)
                result_kind.append({
                    'status': '未開業線',
                    'category': '軌道運送',
                    'operator': unopened_tram_summary['operator'],
                    'distance': unopened_tram_summary['distance']
                })

                # 計
                tram = line_queryset.filter(
                    category=Line.CategoryChoices.TRAM_TRANSPORT
                )
                tram_summary = self.get_summary(tram)
                result_kind.append({
                    'status': '計',
                    'category': '軌道運送',
                    'operator': tram_summary['operator'],
                    'distance': tram_summary['distance']
                })

            result.append({
                'kind': kind,
                'data': result_kind
            })

        return result

    def get_summary(self, queryset):
        return {
            'operator': queryset.values('operator_id').distinct().count(),
            'distance': queryset.aggregate(Sum('distance'))['distance__sum']
        }


class CheckView(SuperUserOnlyMixin, generic.TemplateView):
    template_name = 'library/summary/check.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 整合性
        context['check_object'] = self.get_check_object()

        # 駅情報なし路線
        context['line_no_station_list'] = \
            Line.objects.filter(station__isnull=True, status='active')

        # かな不整合
        context['kana_object'] = self.get_kana_object()

        # 対応データなし
        context['none_object'] = self.get_none_object()

        return context

    def get_check_object(self):
        # 配列初期化
        result = []

        for line in Line.objects.all():
            # 駅が登録されていない場合は除外
            if line.station_set.count() == 0:
                continue

            # 始点エラー
            error_start = line.start != line.station_set.first().name
            # 終点エラ-
            error_end = line.end != line.station_set.last().name
            # キロ程エラー
            error_distance = line.distance != line.station_set.last().distance

            if error_start or error_end or error_distance:
                result.append({
                    'line': line,
                    'error_start': error_start,
                    'error_end': error_end,
                    'error_distance': error_distance
                })

        return result

    def get_kana_object(self):
        kks = pykakasi.kakasi()
        kana_object = []

        for obj in ekidata_models.ConnectOperator.objects.all():
            kana_lib = obj.library_operator.name_kana
            kana_eki_kata = obj.ekidata_operator.company_name_k

            kana_eki_kks = kks.convert(kana_eki_kata)

            kana_eki = ''.join([kks['hira'] for kks in kana_eki_kks])

            if kana_lib != kana_eki:
                kana_object.append({
                    'model': '事業者',
                    'library': obj.library_operator,
                    'library_kana': kana_lib,
                    'ekidata': obj.ekidata_operator,
                    'ekidata_kana': kana_eki,
                })

        for obj in ekidata_models.ConnectStation.objects.all():
            kana_lib = obj.library_station.name_kana
            kana_eki_kata = obj.ekidata_station.station_name_k

            kana_eki_kks = kks.convert(kana_eki_kata)

            kana_eki = ''.join([kks['hira'] for kks in kana_eki_kks])

            if kana_lib != kana_eki:
                kana_object.append({
                    'model': '駅',
                    'library': obj.library_station,
                    'library_kana': kana_lib,
                    'ekidata': obj.ekidata_station,
                    'ekidata_kana': kana_eki,
                })

        return kana_object

    def get_none_object(self):
        none_object = []

        for obj in Operator.objects.all():
            if not ekidata_models.ConnectOperator.objects.filter(
                    library_operator=obj).exists():
                none_object.append({
                    'model': 'ライブラリ／事業者',
                    'object': obj,
                })

        for obj in ekidata_models.Company.objects.filter(e_status=0):
            if not ekidata_models.ConnectOperator.objects.filter(
                    ekidata_operator=obj).exists():
                none_object.append({
                    'model': '駅データ／事業者',
                    'object': obj
                })

        for obj in Station.objects.all():
            if not obj.connectstation_set.exists():
                none_object.append({
                    'model': 'ライブラリ／駅',
                    'object': obj
                })

        for obj in ekidata_models.Station.objects.filter(e_status=0):
            if not obj.connectstation_set.exists():
                none_object.append({
                    'model': '駅データ／駅',
                    'object': obj
                })

        return none_object


class DownloadCSVView(SuperUserOnlyMixin, generic.View):
    """監査用 CSV file を作成
    """
    class OperatorExportResource(ModelResource):
        class Meta:
            model = Operator
            fields = [
                'name', 'name_kana',
                'connectoperator__ekidata_operator__company_name',
            ]
            export_order = fields

    class LineExportResource(ModelResource):
        class Meta:
            model = Line
            fields = [
                'operator__name', 'name', 'name_kana',
                'start', 'end', 'via', 'distance', 'note'
            ]
            export_order = fields

    class StationExportResource(ModelResource):
        class Meta:
            model = Station
            fields = [
                'line__operator__name', 'line__name', 'line__start',
                'line__end', 'name', 'name_kana', 'distance',
                'label', 'freight', 'note'
            ]
            export_order = fields

    def create_ekidata_station_csv(self):
        with StringIO() as f:
            writer = csv.writer(f)

            # header
            writer.writerow([
                'company', 'line', 'station_name', 'grouped_station_list',
                'joined_station_list', 'connected_station_list'
            ])

            # 駅データ路線ごとに処理
            for ekidata_station in ekidata_models.Station.objects.filter(
                    e_status=ekidata_models.Station.EStatusChoices.OPERATED):
                writer.writerow([
                    ekidata_station.line.company.company_name,
                    ekidata_station.line.line_name,
                    ekidata_station.station_name,
                    '|'.join([
                        f'{sta.station_name}（{sta.line.line_name}）' for sta in
                        ekidata_station.grouped_station_list]),
                    '|'.join([
                        sta.station_name for sta in
                        ekidata_station.joined_station_list]),
                    '|'.join([
                        f'{sta.name}（{sta.line}）' for sta in
                        ekidata_station.connected_station_list])
                ])

            # stringIO を返却
            return f.getvalue()

    def get(self, request, *args, **kwargs):
        # response を定義
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=audit_csv.zip'

        # csv ファイルを生成
        with zipfile.ZipFile(
            response,
            mode='w',
            compression=zipfile.ZIP_DEFLATED
        ) as zf:
            zf.writestr('audit_operator.csv',
                        self.OperatorExportResource().export().csv)
            zf.writestr('audit_line.csv',
                        self.LineExportResource().export().csv)
            zf.writestr('audit_station.csv',
                        self.StationExportResource().export().csv)
            zf.writestr('audit_ekidata_station.csv',
                        self.create_ekidata_station_csv())

        return response
