# ステップ0. 環境準備（スマートフォンとAWSサービスを用いた画像認識サービスの構築する）

*当コンテンツは、エッジデバイスとしてスマートフォン、クラウドサービスとしてAWSを利用し、エッジデバイスとクラウド間とのデータ連携とAWSサービスを利用した画像認識を体験し、IoT/画像認識システムの基礎的な技術の習得を目指す方向けのハンズオン(体験学習)コンテンツ「[スマートフォンとAWSサービスを用いた画像認識サービスの構築する](https://qiita.com/kyoso_bizdev/private/e5c252f08de019ab8a1b)」の一部です。*

# ステップ0. 環境準備

今回のハンズオンでは、エッジデバイスであるスマートフォンで表示するWeb画面と、クラウド側で稼働するWebAPIを構築します。

AWS CLIを使ってのコマンドラインでの操作や、プログラムを読み書きする作業は、ブラウザ上で動く統合開発環境サービスである「AWS Cloud9」を使用します。

また、Webページを「AWS Amplify Console」サービスを使って各自のAWS環境にデプロイし、スマートフォンで表示出来ることを確認します。

---

### 目的

- AWS Cloud9 環境を立ち上げ、実際に使ってみる
- AWS CLIを使ってみる
- AWS Amplify Console で WEBアプリケーションのデプロイを行う経験をする

### 概要

- AWSコンソールからCloud9環境を構築する
- AWS CLIを使ってS3にファイルをアップロードする
- AWS Amplify Consoleからシングルページアプリケーションのデプロイを行う

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

AWS Amplify Consoleは、静的WEBサイトあるいはシングルページアプリケーション(SPA)を公開する環境を簡単に作成出来るサービスです。
AWSマネジメントコンソールから設定と操作を行うだけで簡単に公開出来ます。
また、GitHubやCodeCommitなどのリポジトリに接続することで、特定ブランチが更新されると自動的にビルドを行いデプロイを行わせることも可能となり、継続的なアプリケーションのアップデートを行うCI/CD環境を簡単に構築することが出来ます。

- スケーラブルでグローバルなホスティング環境を提供
  - Amazon CloudFront グローバルエッジネットワークを活用
- 対応するアプリケーション
  - 静的サイト(HTML/JavaScript/CSS)
  - SPAフロントエンドのフレームワーク(React、Angular、Vue.js、Ionic、Emberなど)
  - 静的サイトジェネレータ(Gatsby,Eleventy,Hugo,VuePress,Jekyllなど)
  シングルページアプリケーション
- 多様なデプロイ元ソースに対応
  - Gitプロバイダー
    - GitHub,BitBucket.GitLab,AWS CodeCommit
  - Gitプロバイダー以外
    - ブラウザへのドラッグ&ドロップ
    - S3にアップロードしたZIPファイル
    - 外部URL
- 機能ブランチ単位での環境構築
- HTTPSアクセスを標準提供、カスタムドメイン設定も可能
- ユーザ名・パスワードによる限定アクセス設定も可能
- ビルド & デプロイ、ホスティングという 2 つの機能に対して[料金](https://aws.amazon.com/jp/amplify/console/pricing/)が発生
  - ビルド & デプロイ 0.01USD/ビルド分
  - ホスティングサービス 1 GB あたり0.15USD

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

- ターミナルで以下のコマンドを実行し、Githubからソースコードを取得する

```sh
$ git clone https://github.com/IoTkyoto/iot-handson-rekognition

Cloning into 'iot-handson-rekognition'...
remote: Enumerating objects: 369, done.
remote: Counting objects: 100% (369/369), done.
remote: Compressing objects: 100% (324/324), done.
remote: Total 369 (delta 131), reused 210 (delta 29), pack-reused 0
Receiving objects: 100% (369/369), 21.30 MiB | 2.04 MiB/s, done.
Resolving deltas: 100% (131/131), done.
```

- ダウンロードしたリポジトリのWebアプリケーションのディレクトリに移動する

```sh
$ cd iot-handson-rekognition/webapp/
```

### 0-2-3. アプリケーションのProductionビルドを行う

- ターミナルで以下のコマンドを実行し、必要なライブラリファイルをインストールする

```sh
$ npm install
```

※ 処理が終わるまで少し時間がかかります

- ソースコードから静的ファイル(HTML/JavaScript/CSS)を生成する

```sh
$ npm run build
```

### 0-2-4. 静的リソースディレクトリを圧縮する

- 静的リソースディレクトリに移動する

```sh
$ cd dist
```

- フォルダ内のファイル一式をZIP形式で圧縮する

```sh
$ zip -r archive.zip *  
```

### 0-2-5. デプロイファイルを格納するためのS3バケットを作成する

- 圧縮したファイルをAWS環境に格納させるためのS3バケットを作成します
- バケット名は任意の名前にしてください（例：yamada-reko-handson-deployment）

```sh
$ aws s3 mb s3://yamada-reko-handson-deployment
make_bucket: yamada-reko-handson-deployment
```

- 以下のコマンドを実行しS3バケットの一覧にバケットが追加されていることを確認します

```sh
$ aws s3 ls
```

### 0-2-5. S3にファイルをアップロードする

- 圧縮したZipファイルをS3バケットにアップロードします

```sh
$ aws s3 cp archive.zip s3://yamada-reko-handson-deployment/
```

## 0-3. Amplify Consoleでデプロイを行う

### 0-3-1. Amplifyサービスに移動する

- 画面上部の「サービス」をクリックしてください
- 検索窓に「ampl」と入力し、候補から「AWS Amplify」を選択してください
![0-3-1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-3-1.png)

### 0-3-2. アプリケーションの作成を行う

- 画面左のメニューをクリックし「すべてのアプリ」をクリックしてください
![0-3-2_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-3-2_1.png)

- 「アプリの作成」をクリックしてください
![0-3-2_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-3-2_2.png)

### 0-3-3. アプリケーションの設定を行う

- 「Deploy without Git provider」（Gitプロバイダー以外でのデプロイ）を選択し「Continue」をクリックしてください
![0-3-3_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-3-3_1.png)

- 以下の情報を入力し「Save and deploy」をクリックしてください
  - App name（アプリケーション名）
    - 任意（例：yamada_rekognition_handson）
  - Environment name（環境名）
    - 任意（例：prod）
  - Method（デプロイ方法）
    - Amazon S3
  - Bucket（デプロイ対象S3バケット）
    - ステップ0-2-5で作成したデプロイファイル配置用のS3バケット名
    - yamada-reko-handson-deployment
  - Zip file（デプロイ対象ZIPファイル）
    - ステップ0-2-4で作成した圧縮ファイルのファイル名
    - archive.zip
![0-3-3_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-3-3_2.png)
![0-3-3_3](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-3-3_3.png)
    

### 0-3-4. デプロイを実施する

- 処理が進行し「success」が表示されればデプロイが完了です
![0-3-4](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-3-4.png)

### 0-3-5. ブラウザでアクセスする

- Domai部分に表示されているURLをクリックしてください
![0-3-5_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-3-5_1.png)

- 以下のようなページが表示されれば成功です
![0-3-5_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step0/0-3-5_2.png)

### 0-3-6. スマートフォンでハンズオン用アプリを開く

- スマートフォンをインターネットに接続できる状態にし、ブラウザを起動し、ステップ0−3−5でアクセスしたアプリのURLを開いてください
- 以下のようなサイトでURLをQRコード化すると簡単にアクセスすることが出来ます
https://qr.quel.jp/

### 次のステップへ進んでください

- ここまでの作業で事前の準備作業は終了です
- トップページに戻って次のステップに進んでください
