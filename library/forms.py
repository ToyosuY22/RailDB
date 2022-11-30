from django import forms
from django_select2 import forms as s2forms

from library.models import Line, Operator, Station


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
        fields = ['name', 'name_kana', 'distance', 'label', 'note']


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
