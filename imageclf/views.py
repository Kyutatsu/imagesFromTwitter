import os
from django.shortcuts import render
from django.http import HttpResponse

from getImagesFromTwitter.views import get_items_from_tweet
from imageclf.forms import IllustratorForm


APIKEY = os.environ.get('ApiKey_TW')
APISECRETKEY = os.environ.get('ApiSecretKey_TW')


def index(request):
    return HttpResponse('ほげぇ')

def get_and_classify_images(request):
    """twitter user名(@以下)から,可能な限り画像ツイートを回収する。

    回収した画像を分類して表示する。
    """
    if request.method == 'POST':
        form = IllustratorForm(request.POST)
        if form.is_valid():
            twitter_session = OAuth1Session(APIKEY, APISECRETKEY)
            # 初回はmax_idを指定したくない。Noneにすれば指定なしと同じになる。
            max_id = None
            n = 3200 / 200   # ツイート取得可能数
            tweets_with_photo = []
            for i in range(int(n)):
                params = {
                        'screen_name': form.cleaned_data.get('name'),
                        'count': 200,           # 1回のgetにおける最大値
                        'exclude_replies': True,
                        'include_rts': False,
                        'max_id': max_id
                }
                response = twitter_session.get(
                        url='https://api.twitter.com/1.1/statuses/user_timeline.json',
                        params=params
                )
                if response.status_code != 200:
                    return HttpResponse('取得失敗しました')
                tweets = json.loads(response.text)
                # 3,200ツイート以下だった場合、取得できなかった時点で抜ける。
                if tweets == []:
                    break
                for tweetobj in tweets:
                    # twitterは複数種類mediaを同時に添付できないのでidx0のみ見れば良いはず.
                    try:
                        mediatype = tweetobj['extended_entities']['media'][0]['type'] 
                    except Exception:
                        mediatype = None
                    if mediatype and mediatype == 'photo':
                        # mediasはgenerator.
                        medias = get_items_from_tweet(tweetobj)
                        tweets_with_photo.append(medias)
                # 最後(oldest)のtw objectのid由来。
                max_id = tweetobj.get('id') - 1
            if tweets_with_photo == []:
                return HttpResponse('画像はありません')

            # dbへの保存処理ブロック>>わかりにくいから関数化する？
            tweets_for_render = [] # templatでgeneratorが動かないからこうした。書き直したい.
            for medias in tweets_with_photo:
                for media in medias:
                    # 表示用にtextをbynary=>strにする
                    media_cp = media.copy()
                    media_cp['text'] = codecs.decode(media_cp.get('text',''))
                    tweets_for_render.append(media_cp)
                    image = Image(**media)
                    if form.cleaned_data.get('save_status') == 'save':
                        # すでにmediaが存在しないかチェック。
                        existing = Image.objects.filter(
                                media_id_str__exact=media.get('media_id_str')
                        )
                        if existing:
                            texts += '<p>{}はすでに保存されています</p>'.format(
                                    media.get('media_id_str')
                            )
                        else:
                            image.save()
            # 取得した画像の表示
            # redirectした方がいいと思うが、ユーザが使うメソではないので妥協。 
            # >>関数化して、ユーザが使う部分はそれを再利用して作り直す。
            # 画像もdbも一時保存して、それを同定するフラグをurlかsessionで渡す。
            return render(
                request,
                'getImagesFromTwitter/images_list.html', 
                {
                    'tweets': tweets_for_render,
                }

            )
    else:
        form = IllustratorForm()
    # GET時とform.is_varid() == False時はform入力画面へ。
    return render(
            request,
            'getImagesFromTwitter/get_illustrator_name.html',
            {
                'form': form,
            }
    )
