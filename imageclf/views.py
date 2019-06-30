import codecs
import os
import json
import pickle
import numpy as np
import pandas as pd
# from sklearn import 
from requests_oauthlib import OAuth1Session
import requests
from io import BytesIO
import makecsv


from django.shortcuts import render
from django.http import HttpResponse

from getImagesFromTwitter.views import get_items_from_tweet
from imageclf.forms import IllustratorForm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



APIKEY = os.environ.get('ApiKey_TW')
APISECRETKEY = os.environ.get('ApiSecretKey_TW')


def index(request):
    return render(
            request,
            'imageclf/index.html',
            {}
    )

def get_and_classify_images(request):
    """twitter user名(@以下)から,画像ツイートを取得する。

    取得した画像を分類して表示する。
    """
    if request.method == 'POST':
        form = IllustratorForm(request.POST)
        if form.is_valid():
            max_num_img = form.cleaned_data.get('img_number')
            # tweets_with_photo = []  # tweet単位
            tweets_for_render = []  # 画像単位
            twitter_session = OAuth1Session(APIKEY, APISECRETKEY)
            # 初回はmax_idを指定したくない。Noneにすれば指定なしと同じになる。
            max_id = None
            n = 3200 / 200   # ツイート取得可能数
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
                # 3,200ツイート以下だった場合,取得できなかった時点で抜ける。
                if tweets == []:
                    break
                for tweetobj in tweets:
                    # id=0のmediatypeをチェックする.
                    try:
                        mediatype = tweetobj['extended_entities']['media'][0]['type'] 
                    except Exception:
                        mediatype = None
                    if mediatype and (mediatype == 'photo'):
                        # mediasはgenerator.
                        medias = get_items_from_tweet(tweetobj)
                        # 画像ごとのobjectにしてlistに入れる。
                        tweets_for_render.extend(list(medias))
                if len(tweets_for_render) >= max_num_img:
                    break
                max_id = tweetobj.get('id') - 1
            if tweets_for_render == []:
                return HttpResponse('画像はありません')

            if form.cleaned_data.get('clf_status') == 'clf':
                # すでにmediaが存在しないかチェック。
                # process with classifier
                path = os.path.join(BASE_DIR, 'final_tool2.dump')
                with open(path, mode='rb') as f:
                    data = pickle.load(f)
                scaler = data['scaler']
                X_train = data['X_train']
                clf = data['clf']
                scaler.fit(X_train)

                illusts = []
                photos = []

                for media in tweets_for_render:
                    response = requests.get(media['media_url_https'])
                    if response.status_code == 200:
                        fileobj = BytesIO(response.content)
                        temp = makecsv.get_array_from_imgfile(fileobj, color='RGB')
                        mean = np.mean(temp, axis=0)
                        mean = mean.reshape((1,-1))
                        variance = np.var(temp, axis=0)
                        variance = variance.reshape((1,-1))
                        qs = qsorigin = np.percentile(
                                temp,
                                [75, 50, 25],
                                axis=0
                        )
                        qs = qs.reshape((1, -1))
                        features = np.concatenate((mean, variance, qs), axis=1)
                        features_scaled = scaler.transform(features)
                        predict = clf.predict(features_scaled)[0]
                        if predict == 0:
                            proba = clf.predict_proba(features_scaled)[0,0]
                            media['proba'] = round(proba, ndigits=2)
                            illusts.append(media)
                        elif predict == 1:
                            proba = clf.predict_proba(features_scaled)[0,1]
                            media['proba'] = round(proba, ndigits=2)
                            photos.append(media)
            else:  # 分類しない時
                return render(
                    request,
                    'imageclf/show_images.html', 
                    {
                        'images': tweets_for_render,
                    }
                )

            # redirectした方がいい
            illusts = sorted(illusts, key=lambda x: x['proba'], reverse=True)
            photos = sorted(photos, key= lambda x: x['proba'], reverse=True)
            return render(
                request,
                'imageclf/show_images.html', 
                {
                    'illust_data': illusts,
                    'photo_data': photos,
                }
            )
    else:
        form = IllustratorForm()
    # GET時とform.is_varid() == False時はform入力画面へ。
    return render(
            request,
            'imageclf/get_illustrator_name.html',
            {
                'forms': form,
            }
    )
