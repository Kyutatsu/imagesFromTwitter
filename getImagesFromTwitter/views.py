import json
import os
from requests_oauthlib import OAuth1Session
from urllib.parse import parse_qsl


from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
# from getImagesFromTwitter.models import Image
# from getImagesFromTwitter.forms import ImageLabelForm


APIKEY = os.environ.get('ApiKey')
APISECRETKEY = os.environ.get('ApiSecretKey')
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


def index(request):
    request.session['tintin'] = 'otinpo'
    return render(
        request,
        'getImagesFromTwitter/base.html',
        {},
    )


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
        return HttpResponse('token取得成功')
    else:
        return HttpResponse('tokenが取得できません')
