import uuid

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats

from library import models


class OperatorResource(resources.ModelResource):
    class Meta:
        model = models.Operator
        skip_unchanged = True
        import_id_fields = ['id']
        fields = [
            'id', 'name', 'name_kana', 'order'
        ]
        export_order = fields

    def before_import_row(self, row, row_number=None, **kwargs):
        row['id'] = uuid.UUID(row.get('id')) if row.get('id') else None


@admin.register(models.Operator)
class OperatorAdmin(ImportExportModelAdmin):
    formats = [base_formats.CSV]
    resource_classes = [OperatorResource]

    fields = [
        'id', 'name', 'name_kana', 'order'
    ]

    readonly_fields = [
        'id', 'order'
    ]

    list_display = [
        'id', 'name', 'name_kana', 'order'
    ]

    search_fields = [
        'id', 'name', 'name_kana'
    ]


class LineResource(resources.ModelResource):
    class Meta:
        model = models.Line
        skip_unchanged = True
        import_id_fields = ['id']
        fields = [
            'id', 'name', 'name_kana', 'operator', 'start', 'end', 'via',
            'area', 'kind', 'status', 'category', 'distance', 'note', 'order'
        ]
        export_order = fields

    def before_import_row(self, row, row_number=None, **kwargs):
        row['id'] = uuid.UUID(row.get('id')) if row.get('id') else None


@admin.register(models.Line)
class LineAdmin(ImportExportModelAdmin):
    formats = [base_formats.CSV]
    resource_classes = [LineResource]

    fieldsets = [
        ('基本情報', {
            'fields': [
                'id', 'name', 'name_kana', 'operator',
                'start', 'end', 'via', 'distance']
        }),
        ('分類情報', {'fields': ['area', 'kind', 'status', 'category']}),
        ('その他', {'fields': ['note', 'order']}),
    ]

    readonly_fields = [
        'id', 'order'
    ]

    autocomplete_fields = [
        'operator'
    ]

    list_display = [
        'id', 'name', 'name_kana', 'operator', 'start', 'end', 'via',
        'distance', 'area', 'kind', 'status', 'category', 'order'
    ]

    list_filter = [
        'area', 'kind', 'status', 'category'
    ]

    search_fields = [
        'id', 'name', 'name_kana'
    ]


class StationResource(resources.ModelResource):
    class Meta:
        model = models.Station
        skip_unchanged = True
        import_id_fields = ['id']
        fields = [
            'id', 'name', 'name_kana', 'line', 'distance', 'label', 'freight',
            'note', 'order'
        ]
        export_order = fields

    def before_import_row(self, row, row_number=None, **kwargs):
        row['id'] = uuid.UUID(row.get('id')) if row.get('id') else None


@admin.register(models.Station)
class StationAdmin(ImportExportModelAdmin):
    formats = [base_formats.CSV]
    resource_classes = [StationResource]
    fieldsets = [
        ('基本情報', {
            'fields': ['id', 'name', 'name_kana', 'line', 'distance']}),
        ('分類情報', {'fields': ['label', 'freight']}),
        ('その他', {'fields': ['note', 'order']}),
    ]

    readonly_fields = [
        'id', 'order'
    ]

    autocomplete_fields = [
        'line'
    ]

    list_display = [
        'id', 'name', 'name_kana', 'line', 'distance',
        'label', 'freight', 'order'
    ]

    list_filter = [
        'label', 'freight', 'line'
    ]

    search_fields = [
        'id', 'name', 'name_kana'
    ]


class LineRelationshipResource(resources.ModelResource):
    class Meta:
        model = models.LineRelationship
        skip_unchanged = True
        import_id_fields = ['id']
        fields = [
            'id', 'transport_start', 'transport_end',
            'maintenance_start', 'maintenance_end'
        ]

    def before_import_row(self, row, row_number=None, **kwargs):
        row['id'] = uuid.UUID(row.get('id')) if row.get('id') else None


@admin.register(models.LineRelationship)
class LineRelationshipAdmin(ImportExportModelAdmin):
    formats = [base_formats.CSV]
    resource_classes = [LineRelationshipResource]
    fields = [
        'id', 'transport_start', 'transport_end',
        'maintenance_start', 'maintenance_end'
    ]

    readonly_fields = [
        'id'
    ]

    autocomplete_fields = [
        'transport_start', 'transport_end',
        'maintenance_start', 'maintenance_end'
    ]

    list_display = [
        'id', 'transport_start', 'transport_end',
        'maintenance_start', 'maintenance_end'
    ]
