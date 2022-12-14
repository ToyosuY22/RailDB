from django.contrib import admin

from library import models


@admin.register(models.Operator)
class OperatorAdmin(admin.ModelAdmin):
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


@admin.register(models.Line)
class LineAdmin(admin.ModelAdmin):
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


@admin.register(models.Station)
class StationAdmin(admin.ModelAdmin):
    fieldsets = [
        ('基本情報', {
            'fields': ['id', 'name', 'name_kana', 'line', 'distance']}),
        ('分類情報', {'fields': ['label']}),
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
        'label', 'order'
    ]

    list_filter = [
        'label', 'line'
    ]

    search_fields = [
        'id', 'name', 'name_kana'
    ]
