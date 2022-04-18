from django import forms


class ExchangeRateDateForm(forms.Form):

    date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        label='Дата курса валют',
        required=False
    )


class TextFieldForCopyForm(forms.Form):

    text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'id': 'js-copytextarea',
                'rows': '4',
                'readonly': "true",
                'style': "resize: none"
            }
        ),
        label='Текст',
        required=False,
    )
