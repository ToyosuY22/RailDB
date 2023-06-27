# Generated by Django 4.2.2 on 2023-06-25 10:00

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import raildb.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ekidata', '0002_rename_add_station_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='company_name_h',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='事業者名（正式名称）'),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_name_k',
            field=models.CharField(blank=True, max_length=80, null=True, validators=[raildb.validators.KatakanaRegexValidator], verbose_name='事業者名（一般／カナ）'),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_name_r',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='事業者名（略称）'),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_type',
            field=models.IntegerField(blank=True, choices=[(0, 'その他'), (1, 'JR'), (2, '大手私鉄'), (3, '準大手私鉄')], null=True, verbose_name='事業者区分'),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_url',
            field=models.URLField(blank=True, null=True, verbose_name='Webサイト'),
        ),
        migrations.AlterField(
            model_name='company',
            name='e_sort',
            field=models.IntegerField(blank=True, null=True, verbose_name='並び順'),
        ),
        migrations.AlterField(
            model_name='company',
            name='e_status',
            field=models.IntegerField(blank=True, choices=[(0, '運用中'), (1, '運用前'), (2, '廃止')], null=True, verbose_name='状態'),
        ),
        migrations.AlterField(
            model_name='line',
            name='e_sort',
            field=models.IntegerField(blank=True, null=True, verbose_name='並び順'),
        ),
        migrations.AlterField(
            model_name='line',
            name='e_status',
            field=models.IntegerField(blank=True, choices=[(0, '運用中'), (1, '運用前'), (2, '廃止')], null=True, verbose_name='状態'),
        ),
        migrations.AlterField(
            model_name='line',
            name='line_color_c',
            field=models.CharField(blank=True, max_length=6, null=True, validators=[raildb.validators.ColorCodeRegexValidator], verbose_name='路線カラー（コード）'),
        ),
        migrations.AlterField(
            model_name='line',
            name='line_color_t',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='路線カラー（名称）'),
        ),
        migrations.AlterField(
            model_name='line',
            name='line_name_h',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='路線名称（正式名称）'),
        ),
        migrations.AlterField(
            model_name='line',
            name='line_name_k',
            field=models.CharField(blank=True, max_length=80, null=True, validators=[raildb.validators.KatakanaRegexValidator], verbose_name='路線名称（一般／カナ）'),
        ),
        migrations.AlterField(
            model_name='line',
            name='line_type',
            field=models.IntegerField(blank=True, choices=[(0, 'その他'), (1, '新幹線'), (2, '一般'), (3, '地下鉄'), (4, '市電／路面電車'), (5, 'モノレール／新交通')], null=True, verbose_name='路線区分'),
        ),
        migrations.AlterField(
            model_name='line',
            name='lonlat',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='経路表示時の中央'),
        ),
        migrations.AlterField(
            model_name='line',
            name='zoom',
            field=models.IntegerField(blank=True, null=True, verbose_name='路線表示時のGoogleMap倍率'),
        ),
        migrations.AlterField(
            model_name='station',
            name='address',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='住所'),
        ),
        migrations.AlterField(
            model_name='station',
            name='close_ymd',
            field=models.DateField(blank=True, null=True, verbose_name='廃止年月日'),
        ),
        migrations.AlterField(
            model_name='station',
            name='e_sort',
            field=models.IntegerField(blank=True, null=True, verbose_name='並び順'),
        ),
        migrations.AlterField(
            model_name='station',
            name='e_status',
            field=models.IntegerField(blank=True, choices=[(0, '運用中'), (1, '運用前'), (2, '廃止')], null=True, verbose_name='状態'),
        ),
        migrations.AlterField(
            model_name='station',
            name='lonlat',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='緯度軽度'),
        ),
        migrations.AlterField(
            model_name='station',
            name='open_ymd',
            field=models.DateField(blank=True, null=True, verbose_name='開業年月日'),
        ),
        migrations.AlterField(
            model_name='station',
            name='post',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='駅郵便番号'),
        ),
        migrations.AlterField(
            model_name='station',
            name='pref',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ekidata.pref', verbose_name='都道府県'),
        ),
        migrations.AlterField(
            model_name='station',
            name='station_name_k',
            field=models.CharField(blank=True, max_length=80, null=True, validators=[raildb.validators.KatakanaRegexValidator], verbose_name='路線名称（カナ）'),
        ),
        migrations.AlterField(
            model_name='station',
            name='station_name_r',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='駅名称（ローマ字）'),
        ),
    ]