from django.contrib.auth import get_user_model
from django.contrib import admin

from home import models


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('基本情報', {'fields': ['id', 'email', 'display_name']}),
        ('権限情報', {'fields': [
            'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions'
        ]}),
        ('その他', {'fields': [
            'last_login'
        ]}),
    ]

    readonly_fields = [
        'id', 'last_login'
    ]

    filter_horizontal = [
        'groups', 'user_permissions'
    ]

    list_display = [
        'email', 'display_name', 'is_active', 'is_staff', 'is_superuser'
    ]

    list_filter = [
        'is_active', 'is_staff', 'is_superuser'
    ]

    search_fields = [
        'id', 'email', 'display_name'
    ]


@admin.register(models.EmailToken)
class EmailTokenAdmin(admin.ModelAdmin):
    fieldsets = [
        ('基本情報', {'fields': ['id', 'email', 'kind', 'create_user']}),
        ('有効判定情報', {'fields': [
            'create_datetime', 'is_used'
        ]}),
    ]

    readonly_fields = [
        'id', 'create_datetime'
    ]

    autocomplete_fields = [
        'create_user'
    ]

    list_display = [
        'id', 'email', 'kind', 'create_user', 'create_datetime', 'is_used'
    ]

    list_filter = [
        'kind', 'is_used'
    ]

    search_fields = [
        'id', 'email', 'create_user__email'
    ]


@admin.register(models.News)
class NewsAdmin(admin.ModelAdmin):
    fields = [
        'id', 'kind', 'title', 'body', 'update_user', 'update_datetime'
    ]

    readonly_fields = [
        'id', 'update_datetime'
    ]

    autocomplete_fields = [
        'update_user'
    ]

    list_display = [
        'title', 'update_user', 'update_datetime'
    ]

    list_filter = [
        'kind', 'update_user'
    ]

    search_fields = [
        'title', 'body'
    ]


admin.site.site_header = 'RailDB 管理サイト'
