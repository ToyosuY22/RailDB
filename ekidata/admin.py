from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from import_export.formats import base_formats

from ekidata import models


@admin.register(models.Company)
class CompanyAdmin(ExportActionModelAdmin):
    formats = [base_formats.CSV]

    fields = [
        'company_cd', 'rr_cd', 'company_name', 'company_name_k',
        'company_name_h', 'company_name_r', 'company_url', 'company_type',
        'e_status', 'e_sort'
    ]

    readonly_fields = [
        'company_cd'
    ]

    list_display = [
        'company_cd', 'rr_cd', 'company_name', 'company_name_k',
        'company_name_h', 'company_name_r', 'company_url', 'company_type',
        'e_status', 'e_sort'
    ]

    search_fields = [
        'company_cd', 'company_name', 'company_name_k',
        'company_name_h', 'company_name_r'
    ]

    list_filter = [
        'company_type', 'e_status'
    ]


@admin.register(models.Line)
class LineAdmin(ExportActionModelAdmin):
    formats = [base_formats.CSV]

    fields = [
        'line_cd', 'company', 'line_name', 'line_name_k', 'line_name_h',
        'line_color_c', 'line_color_t', 'line_type', 'lonlat', 'zoom',
        'e_status', 'e_sort'
    ]

    readonly_fields = [
        'line_cd'
    ]

    list_display = [
        'line_cd', 'company', 'line_name', 'line_name_k', 'line_name_h',
        'line_color_c', 'line_color_t', 'line_type',
        'e_status', 'e_sort'
    ]

    autocomplete_fields = [
        'company'
    ]

    search_fields = [
        'line_cd', 'line_name', 'line_name_k', 'line_name_h',
    ]

    list_filter = [
        'line_type', 'e_status', 'company'
    ]


@admin.register(models.Station)
class StationAdmin(ExportActionModelAdmin):
    formats = [base_formats.CSV]

    fields = [
        'station_cd', 'station_name', 'station_name_k', 'station_name_r',
        'line', 'pref', 'post', 'address', 'lonlat',
        'open_ymd', 'close_ymd', 'e_status', 'e_sort'
    ]

    readonly_fields = [
        'station_cd'
    ]

    list_display = [
        'station_cd', 'station_name', 'station_name_k', 'station_name_r',
        'line', 'pref', 'post', 'address',
        'open_ymd', 'close_ymd', 'e_status', 'e_sort'
    ]

    autocomplete_fields = [
        'line', 'pref'
    ]

    search_fields = [
        'station_cd', 'station_name', 'station_name_k', 'station_name_r'
    ]

    list_filter = [
        'e_status', 'pref', 'line'
    ]


@admin.register(models.StationGroup)
class StationGroupAdmin(ExportActionModelAdmin):
    formats = [base_formats.CSV]

    fields = [
        'station_g_cd', 'station_set'
    ]

    readonly_fields = [
        'station_g_cd'
    ]

    list_display = [
        'station_g_cd', 'view_str'
    ]

    autocomplete_fields = [
        'station_set'
    ]

    search_fields = [
        'station_g_cd'
    ]

    @admin.display(empty_value='該当なし', description='駅セット')
    def view_str(self, obj):
        return str(obj)


@admin.register(models.Join)
class JoinAdmin(ExportActionModelAdmin):
    formats = [base_formats.CSV]

    fields = [
        'line', 'station_1', 'station_2'
    ]

    list_display = [
        'line', 'station_1', 'station_2'
    ]

    autocomplete_fields = [
        'line', 'station_1', 'station_2'
    ]


@admin.register(models.Pref)
class PrefAdmin(ExportActionModelAdmin):
    formats = [base_formats.CSV]

    fields = [
        'pref_cd', 'pref_name'
    ]

    readonly_fields = [
        'pref_cd'
    ]

    list_display = [
        'pref_cd', 'pref_name'
    ]

    search_fields = [
        'pref_cd', 'pref_name'
    ]


@admin.register(models.ConnectOperator)
class ConnectOperatorAdmin(ExportActionModelAdmin):
    formats = [base_formats.CSV]

    fields = [
        'library_operator', 'ekidata_operator'
    ]

    autocomplete_fields = [
        'library_operator', 'ekidata_operator'
    ]

    list_display = [
        'library_operator', 'ekidata_operator'
    ]


@admin.register(models.ConnectStationGroup)
class ConnectStationGroupAdmin(ExportActionModelAdmin):
    formats = [base_formats.CSV]

    fields = [
        'library_station', 'ekidata_station_group'
    ]

    autocomplete_fields = [
        'library_station', 'ekidata_station_group'
    ]

    list_display = [
        'library_station', 'ekidata_station_group'
    ]
