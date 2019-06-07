from django import forms


class IllustratorForm(forms.Form):
    name = forms.CharField(max_length=100)
    CHOICES = [
            ('clf', '分類する'),
            ('noclf', '分類しない'),
    ]
    clf_status = forms.ChoiceField(
            widget=forms.RadioSelect,
            choices = CHOICES,
    )
