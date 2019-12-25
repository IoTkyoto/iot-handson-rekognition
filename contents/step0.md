# ステップ0. 環境準備（スマートフォンとAWSサービスを用いた画像認識サービスの構築する）

*当コンテンツは、エッジデバイスとしてスマートフォン、クラウドサービスとしてAWSを利用し、エッジデバイスとクラウド間とのデータ連携とAWSサービスを利用した画像認識を体験し、IoT/画像認識システムの基礎的な技術の習得を目指す方向けのハンズオン(体験学習)コンテンツ「[スマートフォンとAWSサービスを用いた画像認識サービスの構築する](https://qiita.com/kyoso_bizdev/private/e5c252f08de019ab8a1b)」の一部です。*

# ステップ0. 環境準備

今回のハンズオンでは、エッジデバイスであるスマートフォンと、クラウド側の構築やその他必要な作業を行うためのローカルPCが必要です。
ハンズオンを進めるにあたって必要な準備作業について説明します。

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
