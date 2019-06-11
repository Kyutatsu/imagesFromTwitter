import codecs
import datetime
import json
import os
from requests_oauthlib import OAuth1Session
from urllib.parse import parse_qsl

from django import forms
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import views
from getImagesFromTwitter.models import Image
from getImagesFromTwitter.forms import ImageLabelForm, IllustratorForm
from getImagesFromTwitter.forms import DisplaySelectForm


APIKEY = os.environ.get('ApiKey_TW')
APISECRETKEY = os.environ.get('ApiSecretKey_TW')
# 開発環境->DEBUG = True, CentOS->DEBUG = Falseで
# 区別するので、以下のように分岐させる。
# settings.pyから読むことはできない。(おそらくここで読む方が先)
DEBUG = os.environ.get('DEBUG')
if DEBUG == 'True':
    oauth_callback = "http://127.0.0.1:8000/getImagesFromTwitter/get_token/"
elif DEBUG == 'False':
    # 後で撮り直す！！
    oauth_callback = "http://qtatsu.com/getImagesFromTwitter/get_token/"
else:
    oauth_callback = "Chack DEBUG vars."


@login_required
def index(request):
    return render(
        request,
        'getImagesFromTwitter/base.html',
        {},
    )


@login_required
def login_twitter(request):
    """OAuth1認証する."""
    twitter_session = OAuth1Session(APIKEY, APISECRETKEY)
    response = twitter_session.post(
            url="https://api.twitter.com/oauth/request_token",
            params={
                'oauth_callback': oauth_callback
            },
    )
    if response.status_code == 200:
        # response.contentはbytesかつxxx=yyy&zzz=qqqという形式なので、パースしてdictへ変換.
        request_token = dict(parse_qsl(response.content.decode('utf-8')))
        auth_url = "https://api.twitter.com/oauth/authenticate"
        auth_endpoint = f"{auth_url}?oauth_token={request_token['oauth_token']}"
        return HttpResponseRedirect(auth_endpoint)
    else:
        return HttpResponse(
                "loginに失敗しました:{}:{}".format(
                    oauth_callback,
                    response.status_code,
                )
        )

@login_required
def get_token(request):
    """login_twitterでtwitter認証画面=>認証完了後, call_backする場所.

    画面としては存在せず、urlのoauth_tokenとverifierの値取得のために利用する.
    developerページに登録してあるのはこの関数へのURL.
    """
    # request.get_full_path()は冗長だったので直接クエリ取った。
    querydict = request.GET
    oauth_token = querydict.get('oauth_token')
    oauth_verifier = querydict.get('oauth_verifier')
    tweet_session = OAuth1Session(
            APIKEY, APISECRETKEY, oauth_token, oauth_verifier
    )
    response = tweet_session.post(
            'https://api.twitter.com/oauth/access_token',
            params={
                'oauth_verifier': oauth_verifier
            },
    )
    if response.status_code == 200:
        access_token = dict(parse_qsl(response.content.decode('utf-8')))
        # sessionにtokenを保存し、login状態を保つ.
        request.session['access_token'] = access_token
        return redirect(to=reverse('getImagesFromTwitter:index'))
    else:
        return HttpResponse('tokenが取得できません')

@login_required
def get_images_from_name(request):
    """twitter user名(@以下)から,可能な限り画像ツイートを回収する。

    複数画像の場合、画像ごとのobjectに分ける。
    """
    if request.method == 'POST':
        form = IllustratorForm(request.POST)
        if form.is_valid():
            # returns tweets.=>一時的にdbに保存...つーか永続保存かな。
                # media_idが被ってた場合排除した方が良さそう。
            # access_tokenはありきで、セッション確率くらいまでdef化けする？
            # かぶってからわければいい？可読性次第だな。
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
                # 3,200ツイート以下だった場合、取得できなかった時点で抜いて効率化する。
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
            texts = '<p>{}個のオブジェクト</p>'.format(len(tweets_with_photo))
            if tweets_with_photo == []:
                return HttpResponse('画像はありません')

            # dbへの保存処理ブロック>>わかりにくいから関数化する？
            tweets_for_render = [] # tempaltでgeneratorが動かないからこうした。書き直したい.
            for medias in tweets_with_photo:
                for media in medias:
                    # 表示用にtextをbynary=>strにする
                    media_cp = media.copy()
                    media_cp['text'] = codecs.decode(media_cp.get('text',''))
                    tweets_for_render.append(media_cp)
                    # PILのImageと同じで紛らわしい名前だから良くない！！
                    # tweet_urlを消す。よくない処理なのでリファクタリングする。
                    media.pop('tweet_url')
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

@login_required
def label_to_images(request):
    """db中のデータのうち、未ラベルのデータを取得してラベルする"""
    ImageLabelFormSet = forms.modelformset_factory(
            Image,
            form=ImageLabelForm,
    )
    allimages = Image.objects.all()
    total_images_number = allimages.count()
    labeled_images_number = allimages.exclude(label__exact=None).count()
    illust_images = allimages.filter(label__exact=0).count()
    photo_images = allimages.filter(label__exact=1).count()
    sc_images = allimages.filter(label__exact=2).count()
    other_images = allimages.filter(label__exact=3).count()
    img_counts = {
            'total': total_images_number,
            'labeled': labeled_images_number,
            'illust': illust_images,
            'photo': photo_images,
            'sc': sc_images,
            'other': other_images,
    }

    if request.method == 'POST':
        # docに従ってここでquery取得したが、これGET時とPOST時の間で他から変更
        # される可能性ないのか？きちんと閉じられているのだろうか?

        # label無しの最も小さいid + 20をmax_idとし
        # 、それ以下をとることで20個取得する。
        no_label_images = Image.objects.filter(label__exact=None)
        if not no_label_images:
            return HttpResponse('未ラベルのサンプルはありません')
        max_id = no_label_images.order_by('id')[0].id + 10
        images = no_label_images.filter(id__lt=max_id)
        formset = ImageLabelFormSet(
                request.POST,
                queryset=images
        )
        if formset.is_valid():
            f = formset.save()
            for image in f:
                # なぜかこれ逆から設定しなければと思ってたけどそんなことなかった。
                image.labeler = request.user
                image.save()
            return redirect(
                    reverse('getImagesFromTwitter:label'),
            )
    else:   # GET時
        # 冗長だし異なるdata取る可能性あるように思うが
        # django公式documentではここでもquery取得してる。
        no_label_images = Image.objects.filter(label__exact=None)
        if not no_label_images:
            return HttpResponse('未ラベルのサンプルはありません')
        max_id = no_label_images.order_by('id')[0].id + 10
        images = no_label_images.filter(id__lt=max_id)
        formset = ImageLabelFormSet(queryset=images)
        # template場でb''をデコードできないのでここで変換する。
        texts = [codecs.decode(img.text) for img in images]
    # template内部でzipできないのでこちらで作った。
    # formsetも別途渡しているのは、management_form部分が必須なので。
    zips = zip(images, formset, texts)
    return render(
            request,
            'getImagesFromTwitter/labeling.html',
            {
                'formset': formset,
                'zips': zips,
                # 'total_images_number': total_images_number,
                # 'labeled_images_number': labeled_images_number,
                'img_counts': img_counts,
            }
    )


@login_required
def display_labeled_images(request):
    """ラベルづけされたイメージを表示する。"""
    if request.method == 'POST':
        form = DisplaySelectForm(request.POST)
        if form.is_valid():
            # choicefieldでstrになってるのでintに戻す
            label = form.cleaned_data.get('label')
            all_images = Image.objects.all()
            images = all_images.filter(label__exact=label)
            return render(
                    request,
                    'getImagesFromTwitter/display_labeled_images_post.html',
                    {'images': images}
            )
    else:
        form = DisplaySelectForm()
    return render(
            request,
            'getImagesFromTwitter/display_labeled_images_get.html',
            {'form': form},
    )



def get_items_from_tweet(tweet):
    """returns dictionaries object of images from a photo-containing tweet object.
    
    for the case that a tweet_obj has several photos, this function returns
    photos object generator.
    """
    twdict = dict()
    medias = tweet.get('extended_entities').get('media')
    for media in medias:
        created_at_text = tweet.get('created_at')
        twdict['created_at'] = datetime.datetime.strptime(
                created_at_text, '%a %b %d %H:%M:%S %z %Y'
        )
        twdict['id_str'] = tweet.get('id_str')
        twdict['screen_name'] = tweet.get('user').get('screen_name')
        twdict['media_id_str'] = media.get('id_str')
        twdict['media_url_https'] = media.get('media_url_https')
        twdict['has_multiple_media'] = True if len(medias) >1 else False
        twdict['text'] = codecs.encode(tweet.get('text'))
        twdict['hashtags_text'] = []
        # entitiesが存在しないかもしれないので、andで繋げ順に評価した。
        if tweet.get('entities') and tweet.get('entities').get('hashtags'):
            for hashtags in tweet.get('entities').get('hashtags'):
                twdict['hashtags_text'].append(hashtags.get('text'))
        twdict['hashtags_text'] = str(twdict['hashtags_text'])
        twdict['retweet_count'] = tweet.get('retweet_count')
        twdict['favorite_count'] = tweet.get('favorite_count')
        twdict['label'] = None
        twdict['labeler'] = None
        # ツイートのurlはなぜか含まれないので、user名,tweetidから自作する。
        pre_url_string = "https://twitter.com/{name}/status/{id}"
        twdict['tweet_url'] = pre_url_string.format(
                **{'name': twdict['screen_name'], 'id': twdict['id_str']}
        )
        # mediaを一つ回すたびにyieldする
        yield twdict
