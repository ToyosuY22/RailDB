import uuid

from django.db import models
from ordered_model.models import OrderedModel
from raildb.validators import KanaRegexValidator


class Operator(OrderedModel):
    class Meta:
        verbose_name = '事業者'
        verbose_name_plural = '事業者'
        ordering = ['order']

    def __str__(self):
        return self.name

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        verbose_name='名称',
        max_length=100
    )

    name_kana = models.CharField(
        verbose_name='名称かな',
        max_length=100,
        validators=[KanaRegexValidator]
    )


class Line(OrderedModel):
    class Meta:
        verbose_name = '路線'
        verbose_name_plural = '路線'
        ordering = ['order']

    def __str__(self):
        name = self.name if self.name else '（路線名なし）'
        return f'{name}（{self.operator}／{self.section}）'

    @property
    def section(self):
        # 区間表示
        if self.via:
            return f'{self.start}─{self.via}─{self.end}'
        else:
            return f'{self.start}─{self.end}'

    @property
    def line_relationship_list(self):
        # 関連路線の一覧を取得
        if self.category in ['train_2', 'tram_transport']:
            return LineRelationship.objects.filter(
                transport_start__line=self
            ).values_list(
                'maintenance_start__line__id', 'maintenance_start__line__name',
                'maintenance_start__line__operator__name',
                'transport_start__name', 'transport_end__name'
            )
        elif self.category in ['train_1', 'train_3', 'tram_maintenance']:
            return LineRelationship.objects.filter(
                maintenance_start__line=self
            ).values_list(
                'transport_start__line__id', 'transport_start__line__name',
                'transport_start__line__operator__name',
                'maintenance_start__name', 'maintenance_end__name'
            )
        else:
            return None

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        verbose_name='名称',
        max_length=100,
        null=True, blank=True
    )

    name_kana = models.CharField(
        verbose_name='名称かな',
        max_length=100,
        validators=[KanaRegexValidator],
        null=True, blank=True
    )

    operator = models.ForeignKey(
        'library.Operator',
        verbose_name='事業者',
        on_delete=models.CASCADE
    )

    start = models.CharField(
        verbose_name='始点',
        max_length=100
    )

    end = models.CharField(
        verbose_name='終点',
        max_length=100
    )

    via = models.CharField(
        verbose_name='経由点',
        max_length=100,
        null=True, blank=True
    )

    class AreaChoices(models.TextChoices):
        JR = 'jr', 'JR'
        HOKKAIDO = 'hokkaido', '北海道運輸局'
        TOHOKU = 'tohoku', '東北運輸局'
        HOKURIKU = 'hokuriku', '北陸信越運輸局'
        KANTO = 'kanto', '関東運輸局'
        CHUBU = 'chubu', '中部運輸局'
        KINKI = 'kinki', '近畿運輸局'
        CHUGOKU = 'chugoku', '中国運輸局'
        SHIKOKU = 'shikoku', '四国運輸局'
        KYUSHU = 'kyushu', '九州運輸局'
        OKINAWA = 'okinawa', '沖縄総合事務局'
        OTHER = 'other', 'その他'

    area = models.CharField(
        verbose_name='運輸局等',
        max_length=10,
        choices=AreaChoices.choices
    )

    class KindChoices(models.TextChoices):
        TRAIN_JR = 'train_jr', '鉄道／普通鉄道〔JR〕'
        TRAIN_ORDINARY = 'train_ordinary', '鉄道／普通鉄道'
        TRAIN_CABLE = 'train_cable', '鉄道／鋼索鉄道'
        TRAIN_SUSPENDED = 'train_suspended', '鉄道／懸垂式鉄道'
        TRAIN_STRADDLE = 'train_straddle', '鉄道／跨座式鉄道'
        TRAIN_GUIDEWAY = 'train_guideway', '鉄道／案内軌条式鉄道'
        TRAIN_TROLLEY = 'train_trolley', '鉄道／無軌条電車'
        TRAM_TRAM = 'tram_tram', '軌道／軌道'
        TRAM_SUSPENDED = 'tram_suspended', '軌道／懸垂式モノレール'
        TRAM_STRADDLE = 'tram_straddle', '軌道／跨座式モノレール'
        TRAM_GUIDEWAY = 'tram_guideway', '軌道／案内軌条式'
        TRAM_MAGLEV = 'tram_maglev', '軌道／浮上式'
        OTHER = 'other', 'その他'

    kind = models.CharField(
        verbose_name='種別',
        max_length=20,
        choices=KindChoices.choices
    )

    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', '開業線'
        UNOPENED = 'unopened', '未開業線'

    status = models.CharField(
        verbose_name='状態',
        max_length=10,
        choices=StatusChoices.choices
    )

    class CategoryChoices(models.TextChoices):
        TRAIN_1 = 'train_1', '第1種鉄道事業'
        TRAIN_2 = 'train_2', '第2種鉄道事業'
        TRAIN_2F = 'train_2f', '第2種鉄道事業（貨物枝線）'
        TRAIN_3 = 'train_3', '第3種鉄道事業'
        TRAM_TRANSPORT = 'tram_transport', '軌道運送事業'
        TRAM_MAINTENANCE = 'tram_maintenance', '軌道整備事業'
        OTHER = 'other', 'その他'

    category = models.CharField(
        verbose_name='事業',
        max_length=20,
        choices=CategoryChoices.choices
    )

    distance = models.IntegerField(
        verbose_name='キロ程',
        help_text='100m単位の整数で入力'
    )

    note = models.TextField(
        verbose_name='備考',
        null=True, blank=True
    )


class Station(OrderedModel):
    class Meta:
        verbose_name = '駅'
        verbose_name_plural = '駅'
        ordering = ['line__order', 'order']

    def __str__(self):
        return f'{self.name}（{self.line}）'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        verbose_name='名称',
        max_length=100
    )

    name_kana = models.CharField(
        verbose_name='名称かな',
        max_length=100,
        validators=[KanaRegexValidator]
    )

    # django-ordered-model: Subset Ordering
    # https://pypi.org/project/django-ordered-model/
    order_with_respect_to = 'line'

    line = models.ForeignKey(
        'library.Line',
        verbose_name='路線',
        on_delete=models.CASCADE
    )

    distance = models.IntegerField(
        verbose_name='キロ程',
        help_text='100m単位の整数で入力',
        null=True, blank=True
    )

    class LabelChoices(models.TextChoices):
        NOT_PASSENGER = 'not_passenger', '旅客扱い無し'
        SEASONAL = 'seasonal', '臨時駅'

    label = models.CharField(
        max_length=20,
        verbose_name='特記事項',
        null=True, blank=True,
        choices=LabelChoices.choices
    )

    class FreightChoices(models.TextChoices):
        FREIGHT = 'freight', '貨物駅'
        ORS = 'ors', 'オフレールステーション'
        OFFICE = 'office', '新営業所'

    freight = models.CharField(
        max_length=20,
        verbose_name='貨物情報',
        null=True, blank=True,
        choices=FreightChoices.choices
    )

    note = models.TextField(
        verbose_name='備考',
        null=True, blank=True
    )


class LineRelationship(OrderedModel):
    class Meta:
        verbose_name = '路線関係'
        verbose_name_plural = '路線関係'
        ordering = ['transport_start__line__order', 'transport_start__order']

    def __str__(self):
        return \
            f'{self.transport_line}→{self.maintenance_line}'

    @property
    def transport_line(self):
        return self.transport_start.line

    @property
    def maintenance_line(self):
        return self.maintenance_start.line

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    transport_start = models.ForeignKey(
        'library.Station',
        verbose_name='運送路線／開始駅',
        related_name='relationship_transport_start',
        on_delete=models.CASCADE
    )

    transport_end = models.ForeignKey(
        'library.Station',
        verbose_name='運送路線／終了駅',
        related_name='relationship_transport_end',
        on_delete=models.CASCADE
    )

    maintenance_start = models.ForeignKey(
        'library.Station',
        verbose_name='整備路線／開始駅',
        related_name='relationship_maintenance_start',
        on_delete=models.CASCADE
    )

    maintenance_end = models.ForeignKey(
        'library.Station',
        verbose_name='整備路線／終了駅',
        related_name='relationship_maintenance_end',
        on_delete=models.CASCADE
    )
