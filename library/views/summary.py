from django.db.models import Sum
from django.views import generic

from library.models import Line, Operator
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
