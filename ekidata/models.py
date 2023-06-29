import uuid

from django.contrib.gis.db import models

from raildb import validators

SRID_WGS84 = 4326


class Company(models.Model):
    class Meta:
        verbose_name = '事業者'
        verbose_name_plural = '事業者'
        ordering = ['e_sort', 'company_cd']

    def __str__(self):
        return self.company_name

    company_cd = models.IntegerField(
        verbose_name='事業者コード',
        primary_key=True,
        unique=True
    )

    rr_cd = models.IntegerField(
        verbose_name='鉄道コード'
    )

    company_name = models.CharField(
        verbose_name='事業者名（一般）',
        max_length=80
    )

    company_name_k = models.CharField(
        verbose_name='事業者名（一般／カナ）',
        max_length=80,
        validators=[validators.KatakanaRegexValidator],
        null=True, blank=True
    )

    company_name_h = models.CharField(
        verbose_name='事業者名（正式名称）',
        max_length=80,
        null=True, blank=True
    )

    company_name_r = models.CharField(
        verbose_name='事業者名（略称）',
        max_length=80,
        null=True, blank=True
    )

    company_url = models.URLField(
        verbose_name='Webサイト',
        null=True, blank=True
    )

    class CompanyTypeChoices(models.IntegerChoices):
        OTHER = 0, 'その他'
        JR = 1, 'JR'
        MAJOR = 2, '大手私鉄'
        SEMIMAJOR = 3, '準大手私鉄'

    company_type = models.IntegerField(
        verbose_name='事業者区分',
        choices=CompanyTypeChoices.choices,
        null=True, blank=True
    )

    class EStatusChoices(models.IntegerChoices):
        OPERATED = 0, '運用中'
        SCHEDULED = 1, '運用前'
        ABOLISHED = 2, '廃止'

    e_status = models.IntegerField(
        verbose_name='状態',
        choices=EStatusChoices.choices,
        null=True, blank=True
    )

    e_sort = models.IntegerField(
        verbose_name='並び順',
        null=True, blank=True
    )


class Line(models.Model):
    class Meta:
        verbose_name = '路線'
        verbose_name_plural = '路線'
        ordering = ['e_sort', 'line_cd']

    def __str__(self):
        return f'{self.line_name}（{self.company}）'

    line_cd = models.IntegerField(
        verbose_name='路線コード',
        primary_key=True,
        unique=True
    )

    company = models.ForeignKey(
        'ekidata.Company',
        verbose_name='事業者',
        on_delete=models.CASCADE
    )

    line_name = models.CharField(
        verbose_name='路線名称（一般）',
        max_length=80
    )

    line_name_k = models.CharField(
        verbose_name='路線名称（一般／カナ）',
        max_length=80,
        validators=[validators.KatakanaRegexValidator],
        null=True, blank=True
    )

    line_name_h = models.CharField(
        verbose_name='路線名称（正式名称）',
        max_length=80,
        null=True, blank=True
    )

    line_color_c = models.CharField(
        verbose_name='路線カラー（コード）',
        validators=[validators.ColorCodeRegexValidator],
        max_length=6,
        null=True, blank=True
    )

    line_color_t = models.CharField(
        verbose_name='路線カラー（名称）',
        max_length=10,
        null=True, blank=True
    )

    class LineTypeChoices(models.IntegerChoices):
        OTHER = 0, 'その他'
        SHINKANSEN = 1, '新幹線'
        NORMAL = 2, '一般'
        SUBWAY = 3, '地下鉄'
        TRAM = 4, '市電／路面電車'
        MONORAIL = 5, 'モノレール／新交通'

    line_type = models.IntegerField(
        verbose_name='路線区分',
        choices=LineTypeChoices.choices,
        null=True, blank=True
    )

    lonlat = models.PointField(
        verbose_name='経路表示時の中央',
        srid=SRID_WGS84,
        null=True, blank=True
    )

    zoom = models.IntegerField(
        verbose_name='路線表示時のGoogleMap倍率',
        null=True, blank=True
    )

    class EStatusChoices(models.IntegerChoices):
        OPERATED = 0, '運用中'
        SCHEDULED = 1, '運用前'
        ABOLISHED = 2, '廃止'

    e_status = models.IntegerField(
        verbose_name='状態',
        choices=EStatusChoices.choices,
        null=True, blank=True
    )

    e_sort = models.IntegerField(
        verbose_name='並び順',
        null=True, blank=True
    )


class Station(models.Model):
    class Meta:
        verbose_name = '駅'
        verbose_name_plural = '駅'
        ordering = ['e_sort', 'station_cd']

    def __str__(self):
        return f'{self.station_name}（{self.line}）'

    station_cd = models.IntegerField(
        verbose_name='駅コード',
        primary_key=True,
        unique=True
    )

    station_name = models.CharField(
        verbose_name='駅名称',
        max_length=80
    )

    station_name_k = models.CharField(
        verbose_name='路線名称（カナ）',
        max_length=80,
        validators=[validators.KatakanaRegexValidator],
        null=True, blank=True
    )

    station_name_r = models.CharField(
        verbose_name='駅名称（ローマ字）',
        max_length=200,
        null=True, blank=True
    )

    line = models.ForeignKey(
        'ekidata.Line',
        verbose_name='路線',
        on_delete=models.CASCADE
    )

    pref = models.ForeignKey(
        'ekidata.Pref',
        verbose_name='都道府県',
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    post = models.CharField(
        verbose_name='駅郵便番号',
        max_length=10,
        null=True, blank=True
    )

    address = models.CharField(
        verbose_name='住所',
        max_length=300,
        null=True, blank=True
    )

    lonlat = models.PointField(
        verbose_name='緯度軽度',
        srid=SRID_WGS84,
        null=True, blank=True
    )

    open_ymd = models.DateField(
        verbose_name='開業年月日',
        null=True, blank=True
    )

    close_ymd = models.DateField(
        verbose_name='廃止年月日',
        null=True, blank=True
    )

    class EStatusChoices(models.IntegerChoices):
        OPERATED = 0, '運用中'
        SCHEDULED = 1, '運用前'
        ABOLISHED = 2, '廃止'

    e_status = models.IntegerField(
        verbose_name='状態',
        choices=EStatusChoices.choices,
        null=True, blank=True
    )

    e_sort = models.IntegerField(
        verbose_name='並び順',
        null=True, blank=True
    )


class StationGroup(models.Model):
    class Meta:
        verbose_name = '駅グループ'
        verbose_name_plural = '駅グループ'
        ordering = ['station_g_cd']

    def __str__(self):
        return '／'.join([str(station) for station in self.station_set.all()])

    station_g_cd = models.IntegerField(
        verbose_name='駅グループコード',
        primary_key=True,
        unique=True
    )

    station_set = models.ManyToManyField(
        'ekidata.Station',
        verbose_name='駅セット'
    )


class Join(models.Model):
    class Meta:
        verbose_name = '接続駅'
        verbose_name_plural = '接続駅'
        ordering = ['station_1__station_cd', 'station_2__station_cd']

    def __str__(self):
        return f'{self.station_1}─{self.station_2}'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    line = models.ForeignKey(
        'ekidata.Line',
        verbose_name='路線',
        on_delete=models.CASCADE
    )

    station_1 = models.ForeignKey(
        'ekidata.Station',
        verbose_name='駅1',
        related_name='join_station_1',
        on_delete=models.CASCADE
    )

    station_2 = models.ForeignKey(
        'ekidata.Station',
        verbose_name='駅2',
        related_name='join_station_2',
        on_delete=models.CASCADE
    )


class Pref(models.Model):
    class Meta:
        verbose_name = '都道府県'
        verbose_name_plural = '都道府県'
        ordering = ['pref_cd']

    def __str__(self):
        return self.pref_name

    pref_cd = models.IntegerField(
        verbose_name='都道府県コード',
        primary_key=True,
        unique=True
    )

    pref_name = models.CharField(
        verbose_name='都道府県名',
        max_length=4,
        unique=True
    )


class ConnectOperator(models.Model):
    class Meta:
        verbose_name = 'DB連携_事業者'
        verbose_name_plural = 'DB連携_事業者'
        ordering = ['library_operator']

    def __str__(self):
        return str(self.library_operator)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    library_operator = models.OneToOneField(
        'library.Operator',
        verbose_name='ライブラリ_事業者',
        on_delete=models.CASCADE
    )

    ekidata_operator = models.OneToOneField(
        'ekidata.Company',
        verbose_name='駅データ_事業者',
        on_delete=models.CASCADE
    )


class ConnectStation(models.Model):
    class Meta:
        verbose_name = 'DB連携_駅'
        verbose_name_plural = 'DB連携_駅'
        ordering = ['library_station', 'ekidata_station']

    def __str__(self):
        return str(self.library_station)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    library_station = models.ForeignKey(
        'library.Station',
        verbose_name='ライブラリ_駅',
        on_delete=models.CASCADE
    )

    ekidata_station = models.ForeignKey(
        'ekidata.Station',
        verbose_name='駅データ',
        on_delete=models.CASCADE
    )
