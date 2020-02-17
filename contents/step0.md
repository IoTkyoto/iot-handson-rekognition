# ステップ0. 環境準備（スマートフォンとAWSサービスを用いた画像認識サービスの構築する）

*当コンテンツは、エッジデバイスとしてスマートフォン、クラウドサービスとしてAWSを利用し、エッジデバイスとクラウド間とのデータ連携とAWSサービスを利用した画像認識を体験し、IoT/画像認識システムの基礎的な技術の習得を目指す方向けのハンズオン(体験学習)コンテンツ「[スマートフォンとAWSサービスを用いた画像認識サービスの構築する](https://qiita.com/kyoso_bizdev/private/e5c252f08de019ab8a1b)」の一部です。*

# ステップ0. 環境準備

今回のハンズオンでは、エッジデバイスであるスマートフォンで表示するWeb画面と、クラウド側で稼働するWebAPIを構築します。

AWS CLIを使ってのコマンドラインでの操作や、プログラムを読み書きする作業は、ブラウザ上で動く統合開発環境サービスである「AWS Cloud9」を使用します。

また、Webページを「AWS Amplify Console」サービスを使って各自のAWS環境にデプロイし、スマートフォンで表示出来ることを確認します。

---

### 目的

- AWSコンソールからクラウドにファイルをアップロードする
- AWS CLIの使い方を学ぶ

### 概要

- AWSコンソールからS3のバケットを作成し画像をアップロードする
- AWS CLI用のユーザーを作成する
- AWS CLIでRekognitionのコレクションを作成し画像を登録する

---

### ＜AWS Cloud9とは？＞

AWS Cloud9は、ブラウザのみでコードを記述、実行、デバッグできるクラウドベースの統合開発環境 (IDE) です。
コードエディタ、デバッガー、ターミナルの機能が含まれています。

Cloud9 IDE はクラウドベースのため、インターネットに接続されたマシンを使用して、オフィス、自宅、その他どこからでもプロジェクトに取り組むことができます。

また、JavaScript、Python、Java など４０を超える一般的なプログラム言語に不可欠なツールがあらかじめパッケージ化されているため、新しいプロジェクトを開始するためにファイルをインストールしたり、開発マシンを設定したりする必要はありません。

- ブラウザのみでコーディングが可能
  - ブラウザのみでアプリケーションを作成、実行、デバッグできる
- リアルタイムにコードの共同編集が出来る
  - 容易にペアプログラミングを行うことが出来る
  - IDE内でのチャットも可能
- サーバーレスアプリケーションの開発環境の構築が簡単に出来る
  - サーバーレス開発に必要なSDK、ライブラリ、プラグインが導入済みの環境がすぐに構築できる
  - AWS Lambda 関数をローカルでテストおよびデバッグするための環境を利用できる
- AWSの各種サービスにターミナルからアクセス可能
  - 事前認証されたAWS CLIがセットアップ済みとなっている
  - ターミナル経由でAWSリソースに対する操作が可能
- Cloud9自体の料金は無料
  - Cloud9を稼働させるEC2インスタンス/EBSボリュームに対してのみ[料金](https://aws.amazon.com/jp/cloud9/pricing/)が発生

より詳しく知りたい場合は[公式サイト](https://aws.amazon.com/jp/cloud9/)をご確認ください。

### ＜AWS CLIとは？＞

AWSコマンドラインインターフェースの略で、AWSサービスをコマンドラインから操作し管理するためのオープンソースツールです。
コマンドラインから複数のAWSサービスを制御し、スクリプトを使用してこれらの作業を自動化することができます。

- Windows/Mac/Linuxなどの様々なOSで使用可能
  - Windowsの場合、PowerShell または Windowsコマンドプロンプトでコマンドを実行
  - Mac/Linux/Unixの場合、bash/zsh/tcshなどの一般的なシェルプログラムでコマンドを実行
- 使い方やリファレンスは以下を参照
  - [AWSコマンドラインインターフェースのユーザーガイド](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-chap-welcome.html)
  - [AWS CLIコマンドリファレンス](https://docs.aws.amazon.com/cli/latest/reference/)

より詳しく知りたい場合は[公式サイト](https://aws.amazon.com/jp/cli/)をご確認ください。

### ＜AWS Amplify Consoleとは？＞

ああああ
ああああ

- あ
- a

より詳しく知りたい場合は[公式サイト](https://aws.amazon.com/jp/amplify/console/)をご確認ください。

---

## 0-1. AWS Cloud9 環境を構築する

AWSコンソールにログインし、AWS Cloud9の環境を構築します。

### 0-1-1. AWSコンソールにログインする
- 各自のアカウントでAWS環境にログインしてください
※ 使用するユーザーには「AdministratorAccess」権限が付与されていることを前提とします
![0-1-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-1-1_1.png)
![0-1-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-1-1_2.png)

- リージョンを「東京」言語を「日本語」に切り替えてください

### 0-1-2. Cloud9サービスに移動する

- 画面上部の「サービス」をクリックしてください
- 検索窓に「cloud」と入力し、候補から「Cloud9」を選択してください
![0-1-2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-1-2.png)

### 0-1-3. Cloud9環境を構築する

- [create environment]（環境を作成する）をクリックしてください
![0-1-3_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-1-3_1.png)

- Nameに「{名前}-handson-env」を入力し、[Next step] をクリックしてください
例）yamada-handson-env
![0-1-3_3](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-1-3_3.png)

- 設定内容はすべてデフォルトのまま画面下部の [Next step] をクリックしてください
![0-1-3_4](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-1-3_4.png)
![0-1-3_5](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-1-3_5.png)

- 設定内容確認画面で [create environment] をクリックしてください
![0-1-3_6](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-1-3_6.png)
![0-1-3_7](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-1-3_7.png)

※ 新しいタブが開き、Cloud9 IDEのCreate処理が行われます
　環境が立ち上がるまでしばらくお待ちください

## 0-2. Webアプリケーションのセットアップを行う
スマートフォンで画面表示するためのWebアプリケーションのセットアップを行います
今回セットアップするアプリケーションは、JavaScriptフレームワークの１つである [Vue.js](https://jp.vuejs.org/index.html) を使った [SPA(シングルページアプリケーション)](https://ja.wikipedia.org/wiki/%E3%82%B7%E3%83%B3%E3%82%B0%E3%83%AB%E3%83%9A%E3%83%BC%E3%82%B8%E3%82%A2%E3%83%97%E3%83%AA%E3%82%B1%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3) と呼ばれるものです

### 0-2-1. ターミナルを開く

- Cloud9 IDE の画面を表示してください
![0-2-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-2-1_1.png)

- Welcomeページを閉じて、新しくターミナルを開いてください
![0-2-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-2-1_2.png)

### 0-2-2. Githubからファイル一式をCloneする




### 0-2-3. アプリケーションのProductionビルドを行う

### 0-2-4. 静的リソースディレクトリを圧縮する

### 0-2-5. S3にファイルをアップロードする


## 0-3. Amplify Consoleでデプロイを行う

### 0-3-1. Amplify Consoleサービスに移動する

### 0-3-2. アプリケーション設定を行う

### 0-3-3. デプロイを実施する

### 0-3-4. ブラウザでアクセスする



### 0-1-5. aaa





## スマートフォンでハンズオン用デモサイトを開く

- スマートフォンをインターネットに接続できる状態にしてください
- ブラウザアプリを起動し、デモアプリのURLを開いてください
- 認証プロンプトが開きますので以下の認証情報を入力してください
- 以下の設定画面が表示されれば問題有りません

## デバイスに必要なモジュールを確認・インストールする

今回のハンズオンを進めるにあたって、デバイス側では以下のモジュールが必要です。

- Python (v3.0以上)
- pip　(Python3用)
- AWS SDK for Python(boto3) (v1.9以上)
- AWS CLI (v1.16以上)
- vim

### Python

Python言語の特徴は、インデント記述により簡潔で見やすいコードや、誰が書いても似たような表記になるシンプルなプログラミング記法、また豊富なモジュールの存在です。

今回のハンズオンではPythonバージョン3を利用しますので、以下の手順に従い、Python3が使用可能か確認してください。

```shell:バージョン確認コマンド
$ python3 --version
```
Pythonはこの後のAWS CLIのインストールにも必要です。
AWS CLIのインストールに対応しているPythonのバージョンは[こちら](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-chap-install.html)をご確認ください。
Pythonバージョン3が入っていない場合や、AWS CLIに対応していないPythonバージョンの場合は、下記サイトを参考に、Pythonバージョン3をインストールしてください。
https://www.python.jp/install/ubuntu/index.html

*この際、OSのアップデートが必要となる可能性もございますのでご注意ください。*

### pip

pipとは、Pythonで書かれたパッケージソフトウェアをインストールしたりする際に利用するパッケージ管理システムです。

デフォルトで設定されているPythonのバージョンが2である場合、Pythonバージョン3に対応したpipが入っていない可能性がありますので、以下のコマンドで確認してください。

```shell:バージョン確認コマンド
$ sudo pip3 --version
```

実行後、`command not found`（「コマンドがない」）と表示された場合、Pythonバージョン3に対応したpipをインストールする必要があります。

```shell:インストール方法
$ sudo apt-get install python3-pip
```

インストール後、pip3コマンドが通ることを確認します。

```shell:バージョン確認コマンド
$ sudo pip3 --version
```

*注意：ここでインストールしたpipを実行する際のコマンドは `pip3`となります。*


### AWS SDK for Python(boto3)
	
boto3とは、AWSサービスをPythonプログラムから操作するためのSDKのライブラリです。
先ほどインストールしたpip3でインストールすることで、python3コマンド実行時に使用可能となります。
		
まず、boto3がインストールされているかを確認してください。

```shell:インストール確認コマンド
$ sudo pip3 list | grep boto3
```

実行結果の出力がない場合は、以下に従い`boto3`をインストールしてください。

```shell:インストールコマンド
$ sudo pip3 install boto3
```

インストール後、再度listコマンドでインストールされていることを確認してください。

```shell:インストール確認コマンド
$ sudo pip3 list | grep boto3
```

### AWS CLI

AWS CLIは、コマンドを利用してAWSのサービスとやり取りすることができるオープンソースツールです。
パッケージ名は `awscli`です。
こちらも上記boto3と同様の方法で、インストールされているかを確認します。

```shell:インストール確認コマンド
$ sudo pip3 list | grep awscli
```

実行結果の出力がない場合は、以下に従い`awscli`をインストールしてください。

```shell:インストールコマンド
$ sudo pip3 install awscli
```

インストール後、再度listコマンドでインストールされていることを確認してください。

```shell:インストール確認コマンド
$ sudo pip3 list | grep awscli
```


#### vimの使用方法について

vimの使用方法が分からない場合は、リンク先の[記事](https://qiita.com/Ichiro_Tsuji/items/e7ff30f0ec0b7d0ceed5#vim%E3%81%A7%E3%83%86%E3%82%AD%E3%82%B9%E3%83%88%E3%82%92%E7%B7%A8%E9%9B%86%E3%81%99%E3%82%8B)に従い、練習問題まで実施してみてください。


## ローカルPCに必要なモジュールを確認・インストールする

今回のハンズオンを進めるにあたって、PC側では以下のモジュールが必要です。

- Python
- AWS CLI

ステップ２で、ローカルPCから`AWS CLI`を使用したAWS Rekognitionの[コレクションの作成](https://docs.aws.amazon.com/ja_jp/rekognition/latest/dg/create-collection-procedure.html)を行う必要があります。
ローカルPCにAWS CLIがインストールされていない場合は、[こちらのサイト](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-chap-install.html)の手順に従いインストールを行ってください。

AWS CLIのインストールには特定のバージョンのPythonが必要ですので、[こちら](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-chap-install.html)をご参考にPythonの有無やバージョンを確認してください。
Pythonが入っていない場合、下記のURLからローカルPCのOSに対応したPythonをインストールしてください。
https://www.python.org/downloads/

**注意1：Pythonプログラムの実行環境の準備について**
今後の手順においてPythonプログラムを作成します。
こちらのプログラムをローカルPCでもテスト実行する場合は、デバイスにインストールされたPython3と同じバージョンのPythonをインストールすることが望ましいです。
また、Pythonプログラムの実行に必要となるboto3などモジュールや、これらをインストールするためのpip3が必要となります。「デバイスに必要なモジュールを確認・インストールする」をご参考にインストールしてください。
