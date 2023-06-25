# Generated by Django 4.2.2 on 2023-06-25 05:40

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import raildb.validators
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('company_cd', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='事業者コード')),
                ('rr_cd', models.IntegerField(verbose_name='鉄道コード')),
                ('company_name', models.CharField(max_length=80, verbose_name='事業者名（一般）')),
                ('company_name_k', models.CharField(max_length=80, null=True, validators=[raildb.validators.KatakanaRegexValidator], verbose_name='事業者名（一般／カナ）')),
                ('company_name_h', models.CharField(max_length=80, null=True, verbose_name='事業者名（正式名称）')),
                ('company_name_r', models.CharField(max_length=80, null=True, verbose_name='事業者名（略称）')),
                ('company_url', models.URLField(null=True, verbose_name='Webサイト')),
                ('company_type', models.IntegerField(choices=[(0, 'その他'), (1, 'JR'), (2, '大手私鉄'), (3, '準大手私鉄')], null=True, verbose_name='事業者区分')),
                ('e_status', models.IntegerField(choices=[(0, '運用中'), (1, '運用前'), (2, '廃止')], null=True, verbose_name='状態')),
                ('e_sort', models.IntegerField(null=True, verbose_name='並び順')),
            ],
            options={
                'verbose_name': '事業者',
                'verbose_name_plural': '事業者',
                'ordering': ['e_sort', 'company_cd'],
            },
        ),
        migrations.CreateModel(
            name='Line',
            fields=[
                ('line_cd', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='路線コード')),
                ('line_name', models.CharField(max_length=80, verbose_name='路線名称（一般）')),
                ('line_name_k', models.CharField(max_length=80, null=True, validators=[raildb.validators.KatakanaRegexValidator], verbose_name='路線名称（一般／カナ）')),
                ('line_name_h', models.CharField(max_length=80, null=True, verbose_name='路線名称（正式名称）')),
                ('line_color_c', models.CharField(max_length=6, null=True, validators=[raildb.validators.ColorCodeRegexValidator], verbose_name='路線カラー（コード）')),
                ('line_color_t', models.CharField(max_length=10, null=True, verbose_name='路線カラー（名称）')),
                ('line_type', models.IntegerField(choices=[(0, 'その他'), (1, '新幹線'), (2, '一般'), (3, '地下鉄'), (4, '市電／路面電車'), (5, 'モノレール／新交通')], null=True, verbose_name='路線区分')),
                ('lonlat', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326, verbose_name='経路表示時の中央')),
                ('zoom', models.IntegerField(null=True, verbose_name='路線表示時のGoogleMap倍率')),
                ('e_status', models.IntegerField(choices=[(0, '運用中'), (1, '運用前'), (2, '廃止')], null=True, verbose_name='状態')),
                ('e_sort', models.IntegerField(null=True, verbose_name='並び順')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ekidata.company', verbose_name='事業者')),
            ],
            options={
                'verbose_name': '路線',
                'verbose_name_plural': '路線',
                'ordering': ['e_sort', 'line_cd'],
            },
        ),
        migrations.CreateModel(
            name='Pref',
            fields=[
                ('pref_cd', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='都道府県コード')),
                ('pref_name', models.CharField(max_length=4, unique=True, verbose_name='都道府県名')),
            ],
            options={
                'verbose_name': '都道府県',
                'verbose_name_plural': '都道府県',
                'ordering': ['pref_cd'],
            },
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('station_cd', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='駅コード')),
                ('station_name', models.CharField(max_length=80, verbose_name='駅名称')),
                ('station_name_k', models.CharField(max_length=80, null=True, validators=[raildb.validators.KatakanaRegexValidator], verbose_name='路線名称（カナ）')),
                ('station_name_r', models.CharField(max_length=200, null=True, verbose_name='駅名称（ローマ字）')),
                ('post', models.CharField(max_length=10, null=True, verbose_name='駅郵便番号')),
                ('add', models.CharField(max_length=300, null=True, verbose_name='住所')),
                ('lonlat', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326, verbose_name='緯度軽度')),
                ('open_ymd', models.DateField(null=True, verbose_name='開業年月日')),
                ('close_ymd', models.DateField(null=True, verbose_name='廃止年月日')),
                ('e_status', models.IntegerField(choices=[(0, '運用中'), (1, '運用前'), (2, '廃止')], null=True, verbose_name='状態')),
                ('e_sort', models.IntegerField(null=True, verbose_name='並び順')),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ekidata.line', verbose_name='路線')),
                ('pref', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ekidata.pref', verbose_name='都道府県')),
            ],
            options={
                'verbose_name': '駅',
                'verbose_name_plural': '駅',
                'ordering': ['e_sort', 'station_cd'],
            },
        ),
        migrations.CreateModel(
            name='StationGroup',
            fields=[
                ('station_g_cd', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='駅グループコード')),
                ('station_set', models.ManyToManyField(to='ekidata.station', verbose_name='駅セット')),
            ],
            options={
                'verbose_name': '駅グループ',
                'verbose_name_plural': '駅グループ',
                'ordering': ['station_g_cd'],
            },
        ),
        migrations.CreateModel(
            name='Join',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ekidata.line', verbose_name='路線')),
                ('station_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_station_1', to='ekidata.station', verbose_name='駅1')),
                ('station_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_station_2', to='ekidata.station', verbose_name='駅2')),
            ],
            options={
                'verbose_name': '接続駅',
                'verbose_name_plural': '接続駅',
                'ordering': ['station_1__station_cd', 'station_2__station_cd'],
            },
        ),
    ]
