from django import forms
from django.core.exceptions import ValidationError
from django_select2 import forms as s2forms

from library.models import Line, LineRelationship, Operator, Station


class UploadForm(forms.Form):
    file = forms.FileField(
        label='CSVファイル',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )


class OperatorForm(forms.ModelForm):
    class Meta:
        model = Operator
        fields = ['name', 'name_kana']


class LineForm(forms.ModelForm):
    class Meta:
        model = Line
        fields = [
            'name', 'name_kana', 'start', 'end', 'via',
            'area', 'kind', 'status', 'category', 'distance', 'note'
        ]


class NameWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains",
        "name_kana__icontains",
    ]


class LineOperatorForm(forms.ModelForm):
    class Meta:
        model = Line
        fields = [
            'operator'
        ]
        widgets = {
            'operator': NameWidget,
        }


class StationForm(forms.ModelForm):
    class Meta:
        model = Station
        fields = ['name', 'name_kana', 'distance', 'label', 'freight', 'note']


class StationLineForm(forms.ModelForm):
    class Meta:
        model = Station
        fields = [
            'line'
        ]
        widgets = {
            'line': NameWidget,
        }


class OrderForm(forms.Form):
    order = forms.IntegerField(
        label='順序',
        min_value=0
    )


class LineRelationshipForm(forms.ModelForm):
    class Meta:
        model = LineRelationship
        fields = [
            'transport_start', 'transport_end',
            'maintenance_start', 'maintenance_end'
        ]
        widgets = {
            'transport_start': NameWidget,
            'transport_end': NameWidget,
            'maintenance_start': NameWidget,
            'maintenance_end': NameWidget
        }

    def clean_transport_end(self):
        # 値を取得
        transport_start = self.cleaned_data.get('transport_start')
        transport_end = self.cleaned_data.get('transport_end')

        # 開始駅と路線が異なる場合は拒否
        if transport_start.line != transport_end.line:
            raise ValidationError(
                '開始駅と路線が異なります', code='invalid'
            )

        # 開始駅の順序以下の場合は拒否
        if transport_start.order >= transport_end.order:
            raise ValidationError(
                '開始駅の順序を超える駅を設定してください', code='invalid'
            )

        # 問題なければ入力された値をそのまま帰す
        return transport_end

    def clean_maintenance_end(self):
        # 値を取得
        maintenance_start = self.cleaned_data.get('maintenance_start')
        maintenance_end = self.cleaned_data.get('maintenance_end')

        # 開始駅と路線が異なる場合は拒否
        if maintenance_start.line != maintenance_end.line:
            raise ValidationError(
                '開始駅と路線が異なります', code='invalid'
            )

        # 開始駅の順序以下の場合は拒否
        if maintenance_start.order >= maintenance_end.order:
            raise ValidationError(
                '開始駅の順序を超える駅を設定してください', code='invalid'
            )

        # 問題なければ入力された値をそのまま帰す
        return maintenance_end
