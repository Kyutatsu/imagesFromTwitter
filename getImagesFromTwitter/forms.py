from django import forms


class ImageLabelForm(forms.Form):
    # 画像のlabel付用のラジオボタンが、Model側から直接設定できないので.
    # widgets = {
    #           'label': forms.RadioSelect(choises=CHOICES)
    # } として、ModelFormつかう方がいいのかもしれない？
    CHOICES = [
            ('1', 'イラスト'),
            ('2', '写真'),
            ('3', 'スクショ'),
    ]
    choice_field = forms.ChoiceField(
            widget=forms.RadioSelect,
            choices=CHOICES,
    )
