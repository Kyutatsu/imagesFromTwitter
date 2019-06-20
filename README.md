# imagesFromTwitter
機械学習とTwitterAPIを利用し、実際に役立つアプリケーションを作成することを目指しました。

## 機能概要
twitterに投稿された画像を閲覧するためのアプリケーションです。機械学習を利用することで、あるユーザが投稿したメディアを**絵と写真別に分けて表示する**ことを可能としました。
![imageclf_gif](https://github.com/Kyutatsu/imagesFromTwitter/blob/staticfiles/imageclf4.gif)

## 背景
twitterではあるユーザのメディア欄という項目からユーザの投稿したメディア一覧を閲覧することが可能なのですが、タグ付けなどの分類機能が弱いという問題がありました。
そのためイラスト投稿ユーザのメディア欄から作品を閲覧する際、ユーザがイラスト以外に日常的な風景の写真などを大量に投稿していた場合にイラストを辿りづらいです。
そこで機械学習を利用し、ユーザが投稿したメディアを絵と写真別に分けて表示することができれば便利であると考えました。


## ファイル（Djangoプロジェクト)の構成
このレポジトリのファイルの説明です。
- getImagesFromTwitter
  - 機械学習に用いるデータをtwitterから取得する、ラベル付けするためのアプリケーションです。開発者が使用するためのものです。
- **imageclf**
  - メインの機能です。twitterのユーザIDを入力すると、学習済みのclassifierオブジェクトを用いて画像を分類します。分類後の画像をクリックすると該当するtweetのページを開きます。
- makecsv.py
  - PILによる画像データの変換に使っているコードです。
- final_tool.dump
  - pickleで保存したpythonオブジェクトです。学習済みcl
## ファイル（Djangoプロジェクト)の構成a
## ファイル（Djangoプロジェクト)の構成A
## ファイル（Djangoプロジェクト)の構成
