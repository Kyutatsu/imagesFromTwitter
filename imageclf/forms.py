from django import forms


class IllustratorForm(forms.Form):
    name = forms.CharField(max_length=100, label="ユーザ ID:")
    CHOICES = [
            ('clf', 'イラスト/写真を分類する'),
            ('noclf', '分類しない'),
    ]
    clf_status = forms.ChoiceField(
            widget=forms.RadioSelect,
            choices = CHOICES,
            label=""
    )
    img_number = forms.IntegerField(
            initial=50,
            label='取得枚数:',
            help_text='取得枚数が多すぎる場合、取得と分類に1,2分かかることがあります。\
                      <br>また画像以外のツイートが非常に多いユーザの場合、\
                      ツイート取得に時間がかかります。<br>\
                      読み込まれない場合、取得枚数を減らしてみてください。'
    )
