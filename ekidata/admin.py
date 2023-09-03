from django.contrib import admin
from django.contrib.gis.geos import Point
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from import_export.widgets import ForeignKeyWidget

from ekidata import models
from library import models as library_models


class CompanyResource(resources.ModelResource):
    class Meta:
        model = models.Company
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ['company_cd']
        fields = [
            'company_cd', 'rr_cd', 'company_name', 'company_name_k',
            'company_name_h', 'company_name_r', 'company_url', 'company_type',
            'e_status', 'e_sort'
        ]


@admin.register(models.Company)
class CompanyAdmin(ImportExportModelAdmin):
    formats = [base_formats.CSV]
    resource_classes = [CompanyResource]

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


class LineResource(resources.ModelResource):
    class Meta:
        model = models.Line
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ['line_cd']
        fields = [
            'line_cd', 'company_cd', 'line_name', 'line_name_k', 'line_name_h',
            'line_color_c', 'line_color_t', 'line_type', 'lonlat',
            'zoom', 'e_status', 'e_sort'
        ]

    company_cd = fields.Field(
        column_name='company_cd',
        attribute='company',
        widget=ForeignKeyWidget(models.Company, field='company_cd'))

    def before_import_row(self, row, row_number=None, **kwargs):
        # lon, lat
        lon = float(row.get('lon'))
        lat = float(row.get('lat'))
        row['lonlat'] = Point(lon, lat)


@admin.register(models.Line)
class LineAdmin(ImportExportModelAdmin):
    formats = [base_formats.CSV]
    resource_classes = [LineResource]

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
        'line_cd', 'line_name', 'line_name_k', 'line_name_h'
    ]

    list_filter = [
        'line_type', 'e_status', 'company'
    ]


class StationResource(resources.ModelResource):
    class Meta:
        model = models.Station
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ['station_cd']
        fields = [
            'station_cd', 'station_g_cd', 'station_name', 'station_name_k',
            'station_name_r', 'line_cd', 'pref_cd', 'post', 'address',
            'lonlat', 'open_ymd', 'close_ymd', 'e_status', 'e_sort'
        ]

    line_cd = fields.Field(
        column_name='line_cd',
        attribute='line',
        widget=ForeignKeyWidget(models.Line, field='line_cd'))

    pref_cd = fields.Field(
        column_name='pref_cd',
        attribute='pref',
        widget=ForeignKeyWidget(models.Pref, field='pref_cd'))

    def before_import_row(self, row, row_number=None, **kwargs):
        # lon. lat
        lon = float(row.get('lon'))
        lat = float(row.get('lat'))
        row['lonlat'] = Point(lon, lat)

        # open_ymd, close_ymd
        # 0000-00-00 の場合は Null とする
        if row.get('open_ymd') == '0000-00-00':
            row['open_ymd'] = None
        if row.get('close_ymd') == '0000-00-00':
            row['close_ymd'] = None


@admin.register(models.Station)
class StationAdmin(ImportExportModelAdmin):
    formats = [base_formats.CSV]
    resource_classes = [StationResource]

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


class JoinResource(resources.ModelResource):
    class Meta:
        model = models.Join
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ['line_cd', 'station_cd1', 'station_cd2']
        fields = ['line_cd', 'station_cd1', 'station_cd2']

    line_cd = fields.Field(
        column_name='line_cd',
        attribute='line',
        widget=ForeignKeyWidget(models.Line, field='line_cd'))

    station_cd1 = fields.Field(
        column_name='station_cd1',
        attribute='station_1',
        widget=ForeignKeyWidget(models.Station, field='station_cd'))

    station_cd2 = fields.Field(
        column_name='station_cd2',
        attribute='station_2',
        widget=ForeignKeyWidget(models.Station, field='station_cd'))


@admin.register(models.Join)
class JoinAdmin(ImportExportModelAdmin):
    formats = [base_formats.CSV]
    resource_classes = [JoinResource]

    fields = [
        'line', 'station_1', 'station_2'
    ]

    list_display = [
        'line', 'station_1', 'station_2'
    ]

    autocomplete_fields = [
        'line', 'station_1', 'station_2'
    ]

    list_filter = [
        'line'
    ]

    search_fields = [
        'station_1__station_name', 'station_1__station_name_k',
        'station_2__station_name', 'station_2__station_name_k'
    ]


class PrefResource(resources.ModelResource):
    class Meta:
        model = models.Pref
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ['pref_cd']
        fields = [
            'pref_cd', 'pref_name'
        ]


@admin.register(models.Pref)
class PrefAdmin(ImportExportModelAdmin):
    formats = [base_formats.CSV]
    resource_classes = [PrefResource]

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


class ConnectOperatorResource(resources.ModelResource):
    class Meta:
        model = models.ConnectOperator
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ['library_operator_id', 'ekidata_operator_cd']
        fields = ['library_operator_id', 'ekidata_operator_cd']

    library_operator_id = fields.Field(
        column_name='library_operator_id',
        attribute='library_operator',
        widget=ForeignKeyWidget(library_models.Operator, field='id'))

    ekidata_operator_cd = fields.Field(
        column_name='ekidata_operator_cd',
        attribute='ekidata_operator',
        widget=ForeignKeyWidget(models.Company, field='company_cd'))


@admin.register(models.ConnectOperator)
class ConnectOperatorAdmin(ImportExportModelAdmin):
    formats = [base_formats.CSV]
    resource_classes = [ConnectOperatorResource]

    fields = [
        'library_operator', 'ekidata_operator'
    ]

    autocomplete_fields = [
        'library_operator', 'ekidata_operator'
    ]

    list_display = [
        'library_operator', 'ekidata_operator'
    ]

    search_fields = [
        'library_operator__name', 'library_operator__name_kana',
        'ekidata_operator__company_name',
        'ekidata_operator__company_name_k',
    ]


class ConnectStationResource(resources.ModelResource):
    class Meta:
        model = models.ConnectStation
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ['library_station_id', 'ekidata_station_cd']
        fields = ['library_station_id', 'ekidata_station_cd']

    library_station_id = fields.Field(
        column_name='library_station_id',
        attribute='library_station',
        widget=ForeignKeyWidget(library_models.Station, field='id'))

    ekidata_station_cd = fields.Field(
        column_name='ekidata_station_cd',
        attribute='ekidata_station',
        widget=ForeignKeyWidget(models.Station, field='station_cd'))


@admin.register(models.ConnectStation)
class ConnectStationAdmin(ImportExportModelAdmin):
    formats = [base_formats.CSV]
    resource_classes = [ConnectStationResource]

    fields = [
        'library_station', 'ekidata_station'
    ]

    autocomplete_fields = [
        'library_station', 'ekidata_station'
    ]

    list_display = [
        'library_station', 'ekidata_station', 'get_e_status'
    ]

    list_filter = [
        'library_station__line', 'ekidata_station__line',
        'ekidata_station__e_status'
    ]

    search_fields = [
        'library_station__name', 'library_station__name_kana',
        'ekidata_station__station_name',
        'ekidata_station__station_name_k',
    ]

    @admin.display(ordering='ekidata_station__e_status', description='状態')
    def get_e_status(self, obj):
        return obj.ekidata_station.get_e_status_display()
