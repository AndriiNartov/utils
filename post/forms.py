import datetime

from django import forms

from .models import Letter, Truck


class LetterCreateForm(forms.ModelForm):
    sending_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        initial=datetime.datetime.now().date(),
        label='Дата отправки'
    )
    truck = forms.ModelChoiceField(
        widget=forms.Select,
        queryset=Truck.objects.all(),
        label='Номер машины'
    )
    track_number = forms.CharField(
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
        label='Номер письма',
        required=False
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '4'}),
        label='Комментарий',
        required=False
    )

    def clean_sending_date(self):
        sending_date_from_filed = self.cleaned_data['sending_date']
        print(datetime.datetime.now().date() < sending_date_from_filed)
        if datetime.datetime.now().date() < sending_date_from_filed:
            raise forms.ValidationError('Дата отправки письма из будущего?')
        return sending_date_from_filed

    class Meta:
        model = Letter
        fields = ('sending_date', 'truck', 'track_number', 'comment')


class LetterUpdateForm(LetterCreateForm):

    status_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        label='Дата(статус)'
    )
    status = forms.ChoiceField(
        widget=forms.Select,
        choices=Letter.STATUSES,
        label='Статус'
    )

    def clean_status_date(self):
        status_date_from_filed = self.cleaned_data['status_date']
        print(datetime.datetime.now().date() < status_date_from_filed)
        if datetime.datetime.now().date() < status_date_from_filed:
            raise forms.ValidationError('Дата статуса письма из будущего?')
        return status_date_from_filed

    class Meta:
        model = Letter
        fields = '__all__'


class LetterDeleteByDateForm(forms.Form):

    date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        label=''
    )