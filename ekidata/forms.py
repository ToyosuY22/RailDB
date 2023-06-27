from django import forms
from django.db.models import TextChoices


class UploadForm(forms.Form):
    class ModeChoices(TextChoices):
        COMPANY = 'company', '事業者'
        LINE = 'line', '路線'
        STATION = 'station', '駅'
        JOIN = 'join', '接続駅'
        PREF = 'pref', '都道府県'
        CONNECT_OPERATOR = 'connect_operator', 'DB連携_事業者'

    mode = forms.ChoiceField(
        label='モード',
        choices=ModeChoices.choices
    )

    file = forms.FileField(
        label='CSVファイル',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )
