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



APIKEY = os.environ.get('ApiKey_TW')
APISECRETKEY = os.environ.get('ApiSecretKey_TW')


def index(request):
    return render(
            request,
            'imageclf/index.html',
            {}
    )

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
            # 一旦変更(後で最大まで直す)
            # n = 3200 / 200   # ツイート取得可能数
            n = 5
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
                    # rendering用の画像obj(自作の辞書)のリスト
                    tweets_for_render.append(media_cp)
                    # Image, PILのImageと同名だからこの名前よくない。
                    # image = Image(**media)
           
            if form.cleaned_data.get('clf_status') == 'clf':
                # すでにmediaが存在しないかチェック。
                # process with classifier
                with open('clf_and_scaler_Xtrain__48feature', mode='rb') as f:
                    data = pickle.load(f)
                # probability=Trueのやつ
                with open('clf7.dump', mode='rb') as f:
                    clf = pickle.load(f)
                scaler = data['scaler']
                X_train = data['X_train']
                # clf = data['clf']
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
                        qsorigin = np.percentile(
                                temp,
                                [75, 50, 25],
                                axis=0
                        )
                        qsorigin = qsorigin.reshape((1,-1))
                        qs = np.percentile(
                                temp,
                                [100,90,80,70,60,50,40,30,20,10,0],
                                axis=0
                        )
                        qs = qs.reshape((1,-1))
                        features = np.concatenate((mean, variance,qsorigin, qs), axis=1)
                        # features = features.reshape((1,-1))
                        features_scaled = scaler.transform(features)
                        predict = clf.predict(features_scaled)[0]
                        if predict == 0:
                            proba = clf.predict_proba(features_scaled)[0,0]
                            media['proba'] = proba
                            illusts.append(media)
                        elif predict == 1:
                            proba = clf.predict_proba(features_scaled)[0,1]
                            media['proba'] = proba
                            photos.append(media)
            else: # 分類しない時
                return render(
                    request,
                    'imageclf/show_images.html', 
                    {
                        'images': tweets_for_render,
                    }
                )

                        # np.arrayの、ndarray[ndarray]でboolianでインデックス指定使いたいので
                       # data_array = ""
                       # for_render_data = ""
                       # for num, media in enumerate(tweets_for_render):
                       #     temp_params = np.array(
                       #         [
                       #             int(media['retweet_count']), 
                       #             int(media['favorite_count']),
                       #             int(media['has_multiple_media']),
                       #         ]
                       #     )
                       #     temp_render_params = np.array(
                       #         [
                       #             media['media_id_str'],
                       #             media['media_url_https'],
                       #             media['text'],
                       #             media['tweet_url'],
                       #         ]
                       #     )
                       #     if num == 0:
                       #         data_array = temp_params.reshape((1,-1))
                       #         for_render_data = temp_render_params.reshape((1,-1))
                       #     else:
                       #         data_array = np.concatenate(
                       #             (data_array, temp_params.reshape((1, -1)))
                       #         )
                       #         for_render_data = np.concatenate(
                       #             (for_render_data, temp_render_params.reshape((1,-1)))
                       #         )
                       # # ここで前のデータ使ってfitしないとダメなの欠陥では？
                       # data_array_norm = scaler.transform(data_array)
                       # classified = knn.predict(data_array_norm)

                        # illust_data = for_render_data[classified=='illust']
                        # photo_data = for_render_data[classified=='photo']

                       #  screen_data = for_render_data[classified=='screen']
            # redirectした方がいい
            illusts = sorted(illusts, key=lambda x: x['proba'], reverse=True)
            photos = sorted(photos, key= lambda x: x['proba'], reverse=True)
            return render(
                request,
                'imageclf/show_images.html', 
                {
                    'illust_data': illusts,
                    'photo_data': photos,
                   #  'screen_data': list(screen_data),
                }
            )
    else:
        form = IllustratorForm()
    # GET時とform.is_varid() == False時はform入力画面へ。
    return render(
            request,
            'imageclf/get_illustrator_name.html',
            {
                'form': form,
            }
    )
