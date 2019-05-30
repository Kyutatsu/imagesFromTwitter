from django import forms
from getImagesFromTwitter.models import Image


class IllustratorForm(forms.Form):
    name = forms.CharField(max_length=100)
    CHOICES = [
            ('save', 'dbに保存する'),
            ('discard', '保存しない'),
    ]
    save_status = forms.ChoiceField(
            widget=forms.RadioSelect,
            choices=CHOICES,
    )


class ImageLabelForm(forms.ModelForm):
    """modelsで直接RadioSelect widgetを選ぶことができないため書き換える
    """
    class Meta:
        model = Image
        CHOICES = [
                (0, 'イラスト'),
                (1, '写真'),
                (2, 'スクショ'),
                (3, 'そのほか'),
        ]
        fields = ('label',)
        widgets = {
                'label': forms.RadioSelect(choices=CHOICES)
        }
