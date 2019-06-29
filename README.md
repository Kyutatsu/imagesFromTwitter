# imagesFromTwitter
機械学習とTwitterAPIを利用し、実際に役立つアプリケーションを作成することを目指しました。
自分は機械学習に関して完全に初学者であったため、Courseraの機械学習コースなどで基本的な考え方を学習しつつ、scikit-learnのdocumentを読んで作成しました。

## 機能概要
twitterに投稿された画像を閲覧できるアプリケーションです。機械学習を利用し、**絵と写真を区別して表示**します。[こちら](https://www.qtatsu.com)からぜひお試しください。

## 使用イメージ
![imageclf_gif](https://github.com/Kyutatsu/imagesFromTwitter/blob/staticfiles/imageclf4.gif)

## 機能と使用技術の一覧
#### 機械学習部分
- 絵/写真の分類
  - scikit-learn
  - NumPy
  - Pandas
- 画像データの取得
  - twitter API
  - requets: pythonのHTTPライブラリ
  - requests_oauthlib: twitterにOauth1認証するためのpythonライブラリ
  - PIL(pillow): pythonの画像加工ライブラリ

#### Webアプリケーション部分
- サーバーサイド
  - Python3
  - Django
- クライアントサイド
  - JavaScript
  - Bootstrap
- インフラ
  - Linux(CentOS7)
  - Apache
  - MySQL
  - mod_wsgi
    - Daemon modeで使用してます。
- その他(デプロイ, バージョン管理, 開発)
  - VPS(独自ドメインを取得し、さくらのVPSを借りて公開しています)
  - SSL(Let's Encrypt)
  - Git
  - Vim
  - Vagrant, VirtualBox: デプロイの練習に使用した。


## 作成した背景
twitterで活動するイラストレーター様の作品を閲覧することを想定しています。

twitterではメディア欄という項目から特定のユーザが投稿したメディア一覧を閲覧することが可能ですが、タグ付けなどの分類機能が弱く、イラスト以外に日常的な風景の写真などを大量に投稿していた場合にイラストを辿りづらいです。

そこで機械学習を利用し、ユーザが投稿したメディアを絵と写真別に分けて表示することができれば便利であると考えました。


## ファイル（Djangoプロジェクト)の構成
このレポジトリのファイルの説明です。
- **imageclf**
  - メインの機能です。twitterのユーザIDを入力すると、学習済みのclassifierオブジェクトを用いて画像を分類します。分類後の画像をクリックすると該当するtweetのページを開きます。
- getImagesFromTwitter
  - 機械学習に用いるデータをtwitterから取得する、ラベル付けするためのアプリケーションです。開発者が使用するために作成したもので、公開していないので使用できません。コードは(あまり良いコードでは無いですが)ご覧いただけます。
- makecsv.py
  - PILによる画像データの変換に使っているコードなどをまとめています。


## 課題
分類精度は写真やイラストのタイプによってかなり異なります。いわゆる漫画、アニメ的な色ぬりをされた絵や、日常風景の写真はかなり正確に分類されます。しかし、厚塗りと言われるような写真チックな塗りをされた絵は、写真だと誤認識されてしまう傾向が強いです。また写真についても、フォトジェニックなもの(水族館など、または人物が「きれいに」写っているもの)は絵だと誤認識される傾向にあります。イラストレーターがアップしたイラスト/写真を利用して作成しましたので、このような結果になっていると思っています。(イラストレーターは動物や食べ物の写真をアップしますが、自撮りなどをあまりアップしません)
また、加工された写真の判定も苦手です。
下記に示したスコアは、あくまでtwitterにあげられがちなイラストや写真の性質に依存したものであり、現実的にはtwitter以外の素材での分類精度はもっと低くなることが予想されます。

なお、分類後のサンプルはスコアが高い順に表示します(上部に表示されるほど、より"絵"や"写真"だとはっきり判断されている)
## 機械学習部分の解説
下図のようにしてデータの収集、ラベリング、trainingを行いました。Testサンプルを用いた評価では、**F1スコアは0.9程度**ありました(マイクロ平均です。"絵"は"写真"の5倍程度のサンプル量があり、precision,recallともに"絵"が高いです。最後の図を参照してください。)。イラストや写真のタイプによって分類精度がかなり異なるのが課題です。
学習モデルはSVM, MLP, Logistic RegressionなどをGridSearchを用いてパラメータを変更しながら試しましたが、対して性能に差は見られませんでした。最終的にはSVMを用いています(カーネルはrbf)。

![image_a](https://github.com/Kyutatsu/imagesFromTwitter/blob/staticfiles/drawing_photo%20(2).jpg)

![image_b](https://github.com/Kyutatsu/imagesFromTwitter/blob/staticfiles/drawing_photo%20(1).jpg)

![image_c](https://github.com/Kyutatsu/imagesFromTwitter/blob/staticfiles/drawing_photo4.jpg)
