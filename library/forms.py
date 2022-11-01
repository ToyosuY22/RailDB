from django import forms


class UploadForm(forms.Form):
    file = forms.FileField(
        label='CSVファイル',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )
