import csv
import io
import traceback
import uuid

from django.contrib import messages
from django.contrib.gis.geos import Point
from django.db import transaction
from django.urls import reverse_lazy
from django.views import generic

from ekidata.forms import UploadForm
from ekidata.models import (Company, ConnectOperator, ConnectStation, Join,
                            Line, Pref, Station, StationGroup)
from library import models as library_models
from raildb.mixins import SuperUserOnlyMixin


class IndexView(SuperUserOnlyMixin, generic.FormView):
    """CSV アップロード
    """
    template_name = 'ekidata/index.html'
    form_class = UploadForm
    success_url = reverse_lazy('ekidata:index')

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
                mode = form.cleaned_data.get('mode')
                if mode == 'company':
                    self.process_company(reader)
                elif mode == 'line':
                    self.process_line(reader)
                elif mode == 'station':
                    self.process_station(reader)
                elif mode == 'join':
                    self.process_join(reader)
                elif mode == 'pref':
                    self.process_pref(reader)
                elif mode == 'connect_operator':
                    self.process_connect_operator(reader)
                elif mode == 'connect_station':
                    self.process_connect_station(reader)
                else:
                    # 想定外の mode が与えられた場合
                    return super().form_invalid(form)
        except Exception as e:
            # エラー内容を表示
            message = traceback.format_exc()
            form.add_error('file', e)
            form.add_error('file', message)
            return super().form_invalid(form)

        # メッセージを追加
        messages.success(self.request, '処理完了しました！')

        return response

    def process_company(self, reader):
        cd_list = []

        # データを追加／更新
        for row in reader:
            obj, _ = Company.objects.update_or_create(
                company_cd=int(row[0]),
                defaults={
                    'rr_cd': row[1],
                    'company_name': row[2],
                    'company_name_k': row[3],
                    'company_name_h': row[4],
                    'company_name_r': row[5],
                    'company_url': row[6],
                    'company_type': row[7],
                    'e_status': row[8],
                    'e_sort': row[9]
                }
            )
            obj.save()
            cd_list.append(obj.company_cd)

        # データを削除
        for obj in Company.objects.all():
            if obj.company_cd not in cd_list:
                obj.delete()

    def process_line(self, reader):
        cd_list = []

        # データを追加／更新
        for row in reader:
            obj, _ = Line.objects.update_or_create(
                line_cd=int(row[0]),
                defaults={
                    'company': Company.objects.get(company_cd=int(row[1])),
                    'line_name': row[2],
                    'line_name_k': row[3],
                    'line_name_h': row[4],
                    'line_color_c': row[5],
                    'line_color_t': row[6],
                    'line_type': row[7],
                    'lonlat': Point(x=float(row[8]), y=float(row[9])),
                    'zoom': row[10],
                    'e_status': row[11],
                    'e_sort': row[12]
                }
            )
            obj.save()
            cd_list.append(obj.line_cd)

        # データを削除
        for obj in Line.objects.all():
            if obj.line_cd not in cd_list:
                obj.delete()

    def process_station(self, reader):
        cd_list = []
        station_group_dict = {}

        # データを追加／更新
        for row in reader:
            obj, _ = Station.objects.update_or_create(
                station_cd=int(row[0]),
                defaults={
                    'station_name': row[2],
                    'station_name_k': row[3],
                    'station_name_r': row[4],
                    'line': Line.objects.get(line_cd=int(row[5])),
                    'pref': Pref.objects.get(pref_cd=int(row[6])),
                    'post': row[7],
                    'address': row[8],
                    'lonlat': Point(x=float(row[9]), y=float(row[10])),
                    'open_ymd': row[11] if row[11] != '0000-00-00' else None,
                    'close_ymd': row[12] if row[12] != '0000-00-00' else None,
                    'e_status': row[13],
                    'e_sort': row[14]
                }
            )
            obj.save()
            cd_list.append(obj.station_cd)

            # 駅グループコード
            station_g_cd = row[1]
            if station_g_cd in station_group_dict:
                station_list = station_group_dict[station_g_cd]
                station_list.append(int(row[0]))
                station_group_dict[station_g_cd] = station_list
            else:
                station_group_dict[station_g_cd] = [int(row[0])]

        # データを削除
        for obj in Station.objects.all():
            if obj.station_cd not in cd_list:
                obj.delete()

        # 駅グループオブジェクトを作成
        for key, value in station_group_dict.items():
            obj, _ = StationGroup.objects.get_or_create(
                station_g_cd=int(key)
            )
            obj.station_set.set(value)
            obj.save()

        # 駅グループオブジェクトを削除
        for obj in StationGroup.objects.all():
            if str(obj.station_g_cd) not in station_group_dict.keys():
                obj.delete()

    def process_join(self, reader):
        obj_list = []

        # データを追加／更新
        for row in reader:
            obj, _ = Join.objects.get_or_create(
                line=Line.objects.get(line_cd=int(row[0])),
                station_1=Station.objects.get(station_cd=int(row[1])),
                station_2=Station.objects.get(station_cd=int(row[2]))
            )
            obj.save()
            obj_list.append({
                'line_id': int(row[0]),
                'station_1_id': int(row[1]),
                'station_2_id': int(row[2])
            })
            print(obj)

        # データを削除
        for obj in Join.objects.all():
            search = {
                'line_id': obj.line.line_cd,
                'station_1_id': obj.station_1.station_cd,
                'station_2_id': obj.station_2.station_cd
            }
            if search not in obj_list:
                obj.delete()

    def process_pref(self, reader):
        cd_list = []

        # データを追加／更新
        for row in reader:
            obj, _ = Pref.objects.update_or_create(
                pref_cd=int(row[0]),
                defaults={
                    'pref_name': row[1],
                }
            )
            obj.save()
            cd_list.append(obj.pref_cd)

        # データを削除
        for obj in Pref.objects.all():
            if obj.pref_cd not in cd_list:
                obj.delete()

    def process_connect_operator(self, reader):
        obj_list = []

        # データを追加／更新
        for row in reader:
            obj, _ = ConnectOperator.objects.get_or_create(
                library_operator=library_models.Operator.objects.get(
                    id=uuid.UUID(row[0])
                ),
                ekidata_operator=Company.objects.get(company_cd=int(row[1]))
            )
            obj.save()
            obj_list.append({
                'library_operator_id': uuid.UUID(row[0]),
                'ekidata_operator_id': int(row[1])
            })

        # データを削除
        for obj in ConnectOperator.objects.all():
            search = {
                'library_operator_id': obj.library_operator.id,
                'ekidata_operator_id': obj.ekidata_operator.company_cd
            }
            if search not in obj_list:
                obj.delete()

    def process_connect_station(self, reader):
        obj_list = []

        # データを追加／更新
        for row in reader:
            if row[1]:
                obj = self.process_connect_station_row(row[1], row[0])
                obj_list.append(obj)
            if row[2]:
                obj = self.process_connect_station_row(row[2], row[0])
                obj_list.append(obj)

        # データを削除
        for obj in ConnectStation.objects.all():
            search = {
                'library_station_id': obj.library_station.id,
                'ekidata_station_id': obj.ekidata_station.station_cd
            }
            if search not in obj_list:
                obj.delete()

    def process_connect_station_row(self, library_obj, ekidata_obj):
        obj, _ = ConnectStation.objects.get_or_create(
            library_station=library_models.Station.objects.get(
                id=uuid.UUID(library_obj)
            ),
            ekidata_station=Station.objects.get(
                station_cd=int(ekidata_obj)
            )
        )
        obj.save()

        return {
            'library_station_id': uuid.UUID(library_obj),
            'ekidata_station_id': int(ekidata_obj)
        }


class DetailLineView(generic.DetailView):
    template_name = 'ekidata/detail_line.html'
    model = Line
