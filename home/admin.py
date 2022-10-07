from django.contrib import admin
from home import models


@admin.register(models.User)
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
        ('基本情報', {'fields': ['id', 'email', 'kind', 'created_user']}),
        ('有効判定情報', {'fields': [
            'created_datetime', 'is_used'
        ]}),
    ]

    readonly_fields = [
        'id', 'created_datetime'
    ]

    autocomplete_fields = [
        'created_user'
    ]

    list_display = [
        'id', 'email', 'kind', 'created_user', 'created_datetime', 'is_used'
    ]

    list_filter = [
        'kind', 'is_used'
    ]

    search_fields = [
        'id', 'email', 'created_user__email'
    ]


admin.site.site_header = 'RailDB 管理サイト'
