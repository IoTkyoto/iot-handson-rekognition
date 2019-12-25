---
title: ステップ4. ログデータをクラウドにアップロードする（ZyboとAWSサービスを用いてデバイスとクラウドの双方向通信とデータの可視化・分析を行う）
tags: IoT AWS zybo ubuntu16.04 Python3
author: kyoso_bizdev
slide: false
---
*当記事は、エッジデバイスとしてZybo(OS:ubuntu)を、クラウドサービスとしてAWSを利用し、エッジデバイスとクラウド間との連携を本格的に体験し、IoTシステムの基礎的な技術の習得を目指す方向けのハンズオンコンテンツ記事「[ZyboとAWSサービスを用いてデバイスとクラウドの双方向通信とデータの可視化・分析を行う](https://qiita.com/kyoso_bizdev/private/e5c252f08de019ab8a1b)」の一部です。*

# ステップ4. ログデータをクラウドにアップロードする

![ステップ4アーキテクチャ図](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/architecture_step4.png)

ステップ4では、前回までのステップでWeb APIから受け取った認証結果データや分析データ、デバイス側で取得したセンサー値データを、クラウドに送信し蓄積する仕組みを構築します。
データを格納することで、次のステップでデータの可視化が行えるようになります。

AWS IoT Coreで作成したトピックに対して、デバイスからHTTPアクセスで各種データを送信します。
次にIoT Coreでルールを作成します。
このルールは待ち受けているトピックで受信したデータをDynamo DBやS3に格納するように設定します。

顔画像分析ログデータについては、各所から集められる大量のストリーミングログデータを欠損なく扱うユースケースとして、[Amazon Kinesis Data Firehose](https://aws.amazon.com/jp/kinesis/data-firehose/)経由でデータの保存を行います。

今回の手順では、先にデータの格納先を準備し、次にルールを作成、最後にデバイスからログデータを送信するPythonプログラムを作成します。

**注意：今回のIoT通信の方法について**
ここではIoTで通常よく使われるMQTT通信ではなく、HTTP通信を利用します。
またデバイス側でのトピックのサブスクライブは行わず、トピックへのパブリッシュ（データ送信）のみ実施します。

---

### 目的

- デバイス側のデータをクラウドに送信する手法を学ぶ
- AWSでのデータ蓄積方法を学ぶ
- AWSでのデータ収集環境を構築する

### 概要

- デバイス側で発生したログ情報をクラウドにアップロードする
- AWS IoT Coreを使用する（HTTPアクセス）
- 以下のログデータを送信する（別トピックとして）
	- センサー値のリアルタイムデータ -> DynamoDBのテーブルに格納
	- 認証ログデータ -> S3バケットに格納
	- 応用編：自動ドア開閉ログデータ -> S3バケットに格納
	- 顔画像分析ログデータ -> Kinesis Data Firehose経由 -> S3バケットに格納

---

### ＜Amazon DynamoDBとは？＞

Amazon DynamoDBとは、AWSが提供する完全マネージド型のNoSQLデータベースサービスです。
1日に10兆件以上のリクエストを処理することができ、毎秒2,000万件を超えるリクエストをサポートします。
また、スキーマレスなデータベースのため、テーブル作成時にテーブル名とプライマリキー以外の指定は必要ありません。
IoTと非常に親和性が高く、下記のような特徴があります。

- Key-value およびドキュメントデータモデル
- サイジング不要、I/Oスループットのみ指定する
- スキーマレス、KEYが増えてもマイグレーションしなくていい
- SQLではなくAPIで利用する。ストリームデータを連続的に書き込みつつ即座に読み出すようなことは得意領域。一方、SQLが得意とする複雑な処理は苦手
- テーブル内のデータの追加・変更をトリガーにコードを実行することができる(DynamoDB Streams -> Lambda)
- indexの張り方に失敗すると痛い目に遭う。LSI/GSIの使い分けが難しい
- 1回のQueryで取得できるデータが約1MBに制限されている

より詳しく知りたい場合は[公式サイト](https://aws.amazon.com/jp/dynamodb/)をご確認ください。


### ＜AWS IoT Coreとは？＞

AWS IoT Coreは、インターネットに接続されたデバイスから、クラウドアプリケーションやその他のデバイスに簡単かつ安全に通信するためのフルマネージド型クラウドサービスです。
AWS IoT Core を使用すると、AWS Lambda、Amazon Kinesis、Amazon S3、Amazon SageMaker、Amazon DynamoDB、Amazon CloudWatch、AWS CloudTrail、Amazon QuickSight といった AWS の各種サービスを簡単に使用できます。
これにより、インフラストラクチャの管理をせずに、接続されたデバイスで生成されたデータを収集、処理、分析し、そのデータに基づいてアクションを起こすIoTアプリケーションを構築できます。

- 認証と認可
    - 接続するすべてのポイントでの相互認証と暗号化が提供されており、デバイスとAWS IoT Core間では身元が証明されたデータのみが交換される
    - AWSの認証方法(「SigV4」と呼ばれる)、X.509証明書ベースの認証、お客様が作成したトークンベースの認証(カスタムオーソライザーを使用)がサポートされている
- ルールエンジン
    - コーディング不要で作成したビジネスルールに基づいてメッセージを各種AWSサービスに配信することが出来る
    - １つのデバイスからのデータだけでなく多数のデバイスからのデータにも同じルールを適用できる
- デバイスシャドウ
    - それぞれのデバイスについて「シャドウ」、つまり永続的な仮想バージョンを作成できる
    - デバイスがオフライン状態のときでも、各デバイスについて最後に報告された状態と希望する今後の状態が保持されている

より詳しく知りたい場合は[公式サイト](https://aws.amazon.com/jp/iot-core)をご確認ください。

### ＜Amazon Kinesis Data Firehoseとは？＞

Amazon Kinesis Data Firehoseは、数十万のデータソースから継続的に生成されるようなリアルタイムなストリーミングデータを、データストアや分析ツールにロードするためのフルマネージド型のクラウドサービスです。
フルマネージドサービスのため、データスループットに応じて自動的にスケールされ、継続的な管理は不要です。
また、ロード前にデータのバッチ処理、圧縮処理、暗号化が行われるため、送信先でのストレージ量を最小化し、セキュリティを強化できます。
Kinesis Data Firehoseでは、同じAWSリージョン内にある3つの拠点でデータが同期的に複製されるため、データ転送時の高い可用性と耐久性を確保できます。

- 総合的なストリーム管理機能
    - スケーリング、シャーディング、モニタリングなど、データを指定された間隔で継続的にデスティネーションにロードするためのストリーム管理全般が提供される
- 選択可能なロード先
    - Amazon S3
    - Amazon Redshift
    - Amazon Elasticsearch Service
    - Splunk
- サーバーレスのデータ変換
    - データソースからの生のストリーミングデータを送信先のデータストアで必要なフォーマットに簡単に変換出来る
- フルマネージドサービス
    - ストリーミングデータのロードに必要なコンピューティング、メモリ、ネットワークリソースのプロビジョニング、管理、スケーリングが自動的に実行される

より詳しく知りたい場合は[公式サイト](https://aws.amazon.com/jp/kinesis/data-firehose/)をご確認ください。

## 4-1. センサーデータを格納するためのDynamoDBテーブルを作成

センサーデータをクラウドに蓄積し後続のステップで時系列データのリアルタイム可視化を行うために、DynamoDBのテーブルを作成します。

- 下記の内容でDynamoDBのテーブルを作成してください。
  - テーブル名：任意の名称（例： `yamada_sensor_data_table`）
  - プライマリキー： 
     - パーティションキー：`DeviceID` 文字列
     - ソートキー：`Datetime` 文字列
  - 読み込みキャパシティーユニット： `1`
  - 書き込みキャパシティーユニット： `1`

---

#### ＜テーブルのプライマリキーとは？＞
DynamoDBはプライマリキーを使用してテーブルの各項目を一意に識別します。
そのため、２つのデータが同じプライマリキーを持つことは出来ません。
プライマリキーには以下の２種類の指定の仕方があります。

- パーティションキー
  - パーティションキーという１つの属性で構成されたシンプルなプライマリキー
  - 内部でハッシュ化してハッシュごとにデータを分散保管するために使用します
- パーティションキー ＋ ソートキー
  - 複合プライマリキーとも呼ばれます
  - 同じパーティションキー値を持つすべてのデータはソートキー値でソートされてまとめて保存されます
  - ソートキー値で並べ替えられた順にDynamoDBが同じパーティションキーを持つデータどうしを物理的に近くに保存します

https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html#HowItWorks.CoreComponents.PrimaryKey

#### ＜キャパシティーユニットとは？＞
DynamoDBでは、データの読み書きの度に料金がかかります。
事前に読み込み、書き込み別にキャパシティーユニットを割り当てておく必要があり、事前に割り当てたキャパシティーユニットを超えて利用した場合はエラーが発生します。
ただし、未使用のキャパシティーはバーストキャパシティーとして最大5分(300秒)保持し使用されます。
キャパシティーユニットのオンデマンドモードを指定した場合は、リクエストに応じて自動的に拡張・縮小されます。

- 読み込みキャパシティーユニット
  - 最大サイズ4KBの項目について1秒あたり1回の強力な整合性のある読み込み 又は 1秒あたり2回の結果整合性のある読み込みが可能
  - 4KB未満のレコードはレコード毎に4KBに切り上げられて計算される
- 書き込みキャパシティーユニット
  - 最大サイズ1KBまでの項目について、1秒あたり 1回の書き込みが可能
  - 1KB未満のレコードはレコード毎に1KBに切り上げられて計算される

https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/HowItWorks.ReadWriteCapacityMode.html

---

- AWSのコンソール画面で「DynamoDB」を検索・選択し、[テーブルの作成]をクリックしてください
![4-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-1_1%E6%9E%9A%E7%9B%AE.png)

- テーブル名、プライマリキー(パーティションキー＋ソートキー)を設定してください
![4-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-1_2%E6%9E%9A%E7%9B%AE.png)

- テーブル設定のデフォルト設定のチェックを外してください
![4-1_3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-1_3%E6%9E%9A%E7%9B%AE.png)

- AutoScallingの読み込み、書き込みのチェックを外して、プロビジョニングされたキャパシティにそれぞれ「1」を設定し「作成」をクリックしてください
![4-1_4](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-1_5%E6%9E%9A%E7%9B%AE.png)

- 画面左メニューの「テーブル」を選択し、一覧に作成したテーブルが表示されていることを確認してください


## 4-2. センサーデータをDynamoDBに格納するルールを作成
 
これにより、特定のトピックにデータが届いた事をトリガーにしたアクションを実行することが出来ます。
今回は「ステップ4-1で作成したテーブルに届いたデータを格納する」というアクションを設定します。

- AWSのコンソールで[IoT Core]のサービス画面に遷移し、下記の通りに設定してください。
  - ルール名：任意の名称（例： `yamadaPutSensorDataToDynamoDB`）
  - 説明：任意
  - ルールクエリステートメント： `SELECT*FROM 'handson/sensorLogData'`

---

#### ＜ルールとは？＞

AWS IoTでは、ルールはSQLに似た構文を使用して定義されています。
SQLステートメントは３つのタイプの句で構成されます。

- SELECT
  - 受信メッセージのペイロードから情報を抽出して変換を行う
- FROM
  - メッセージのトピックフィルター
  - ここで指定されたフィルターに一致するトピックに送信されたメッセージを対象とする
- WHERE
  - ルールで指定されたアクションが実行されるかどうかを決定する条件付きロジック

今回使用するクエリは「`SELECT*FROM 'handson/sensorLogData'`」ですので、「handson/sensorLogData」トピックのメッセージの全文にアクションを適用する意味となります。

使用出来る構文は以下をご参照ください。
https://docs.aws.amazon.com/ja_jp/iot/latest/developerguide/iot-sql-reference.html

#### ＜アクションとは？＞

AWS IoTでは、ルールがトリガーされたときに行う動作を指定するためにアクションが使用されます。
アクション実行時にエラーが発生した場合は複数回の試行を行い、一定回数の試行後にメッセージを破棄し、エラーアクションが実行されます。

- 現時点(2019/8/1)では以下のアクションがサポートされています。
  - DYNAMODB：DynamoDBテーブルにメッセージを１項目として書き込む
  - DYNAMODBv2：DynamoDBテーブルの複数列にメッセージを分割し書き込む
  - LAMBDA：指定したLambda関数を呼び出し、メッセージをパラメータとして渡す
  - SNS：メッセージをSNSトピック送信する
  - SQS：メッセージをSQSキューに送信する
  - AMAZON KINESIS：メッセージをKinesisストリームに送信する
  - AWS IOTの再パブリッシュ：メッセージをAWS IoTのトピックに再パブリッシュする
  - S3：メッセージをS3バケットに格納する
  - AMAZON KINESIS FIREHOSE：メッセージをKinesi Firehoseストリームに送信する
  - CLOUDWATCHメトリクス：Cloudwatchメトリクスにデータを送信する
  - CLOUDWATCHアラーム：Cloudwatchアラームの状態を変更する
  - AMAZON ELASTICSEARCH：Amazon Elasticsearchサービスにメッセージを送信する
  - IOT ANALYTICS：メッセージからAWS IoT Analyticsチャネルにデータを送信する
  - IOT EVENTS：メッセージからAWS IoTイベント入力にデータを送信する
  - ステップ関数：Step Functionsステートマシンの実行を開始する
  - SALESFORCE：SalesforceのIoT入力ストリームにメッセージを送信する

https://docs.aws.amazon.com/ja_jp/iot/latest/developerguide/iot-rule-actions.html

---

- AWSのコンソール画面で**IoT Core**を検索・選択し、左側メニューの[ACT]をクリックしてください
- ルール一覧画面の右上の[作成]をクリックしてください
![4-2_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-2_1%E6%9E%9A%E7%9B%AE.png)

- 「名前」「ルールクエリステートメント」を設定し[アクションの追加]をクリックしてください
![4-2_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-2_2%E6%9E%9A%E7%9B%AE.png)


次に「アクション」として、ステップ4-1で作成したDynamoDBテーブルにデータを格納させる設定を行います。
今回のアクションの実行に必要なロールを自動作成・アタッチし、最後にルールの作成を完了させます。

- アクションの選択で「データベーステーブル(DynamoDBv2)の複数列にメッセージを分割する」にチェックを付け[アクションの設定]をクリックしてください
![4-2_3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-2_3%E6%9E%9A%E7%9B%AE.png)

- アクションの設定で「テーブル名」に4-1で作成したDynamoDBテーブルを指定し[ロールの作成]をクリックしてください
![4-2_4](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-2_4%E6%9E%9A%E7%9B%AE.png)

- 新しいロールの作成画面で「名前」に任意の名称（例：yamada_sensor_log_data_role）を入力し[ロールの作成]をクリックしてください
![4-2_5](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-2_5%E6%9E%9A%E7%9B%AE.png)

- ロールが作成されたことを確認し[アクションの追加]をクリックしてください
![4-2_6](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-2_6%E6%9E%9A%E7%9B%AE.png)

- 最後に[ルールの作成]をクリックしてください
![4-2_7](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-2_7%E6%9E%9A%E7%9B%AE.png)

- ルール一覧画面に作成したルールが追加されたことを確認してください


## 4-3. センサーデータをDynamoDBに格納するルールの動作を確認

ステップ4-2で作成したルールが期待通りの動作をするか、AWSのコンソールからトピックを指定しメッセージを発行(パブリッシュ)してテストしてみましょう。

- 左のメニューの[テスト]をクリックしてください
- 画面下部の発行部分に、対象のトピック名とテストで発行したいJSONデータを入力してください
- [トピックに発行]をクリックしてください
![4-3_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-3_1%E6%9E%9A%E7%9B%AE.png)


- テストデータ
  - [センサーデータ]トピック名： `handson/sensorLogData`
  - JSONデータ：

```json
{
	"DeviceID": "id001",
	"Datetime": "2019-01-01T00:00:00Z",
	"Value": 40
}
```

- DynamoDBのコンソール画面を開いて、対象のテーブルを確認し、データが格納されていることを確認してください
![4-3_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-3_2%E6%9E%9A%E7%9B%AE.png)

#### 【注意】 ルールの動作確認が終わったら、テストデータは削除しましょう
このステップでテストとしてパブリッシュしたデータはダミーデータです。本来のデータと混ざり合ってしまうと、ステップ5での可視化に影響が出ますので、必ず削除しましょう。

ステップ4-1で作成したDynamoDBテーブル （例： `yamada_sensor_data_table`）の項目一覧から、テストで送信したデータ項目にチェックを入れ、[アクション]から[削除]を行なってください。

## 4-4. 認証ログデータ・顔分析ログデータ・開閉ログデータを格納するためのS3バケットを作成

前のステップでは、データの格納先の作成、IoT Coreのルール・アクションの作成、そしてルールで指定したトピックへのテストデータの送信、というIoT Coreで必要な操作を一通り行いました。
次は、同様の流れで、各種ログデータを保存するためのS3バケットを作成し、ルール・アクションを作成、そしてテストデータの送信を行います。

以降バケット名に言及する際は「認証ログデータ格納用バケット」, 「顔分析ログデータ格納用バケット」, 「開閉ログデータ格納用バケット」と表記します。

- 下記の設定を見ながら各種用途別に作成してください

  - **認証ログデータ格納用バケット**
    - バケット名：全世界で一意となる任意の名称(例: `yamada-auth-log-data`)
    - 設定： デフォルト(非公開設定)
  - **顔分析ログデータ格納用バケット**
    - バケット名：全世界で一意となる任意の名称(例: `yamada-analysis-log-data`)
    - 設定： デフォルト(非公開設定)
  - **開閉ログデータ格納用バケット**
    - バケット名：全世界で一意となる任意の名称(例: `yamada-door-open-log-data`)
    - 設定： デフォルト(非公開設定)

- S3バケットの作成方法が分からない場合は、ステップ１をご確認ください

## 4-5. S3バケットにログデータを格納するルールを作成

下記は「認証ログデータ」を例として説明しています。
この手順を「開閉ログデータ」に読み替えて、同じようにルールを作成してください。

「顔分析ログデータ」はKinesis Data Firehose経由でS3にデータ格納しますので、次ステップ4-6で解説します。

- 認証ログデータ
    - ルール名：任意の名称（例： `yamadaPutAuthLogDataToS3`）
    - 説明： 任意
    - ルールクエリステートメント： `SELECT*FROM 'handson/authLogData'`
- 開閉ログデータ
    - ルール名：任意の名称（例： `yamadaPutDoorOpenLogDataToS3`）
    - 説明： 任意
    - ルールクエリステートメント： `SELECT*FROM 'handson/doorOpenLogData'`


ステップ4-2を参考に、新たなルールを下記の通りに設定してください。

![4-5_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-5_1%E6%9E%9A%E7%9B%AE.png)

次に、「アクション」として、ステップ4-4で作成した各種S3バケット（今回の例では認証ログデータバケットが対象）に対し、データを格納していくよう設定します。

- 「Amazon S3バケットにメッセージを格納する」にチェックを付けて[アクションの設定]をクリックしてください
![4-5_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-5_2%E6%9E%9A%E7%9B%AE.png)

- 対象のS3バケット名、キー名を入力し、「ロールの作成」で新しいロールを作成し[アクションの追加]をクリックしてください
![4-5_3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-5_3%E6%9E%9A%E7%9B%AE.png)

#### ＜キーとは？＞
「キー」は、S3バケットに格納されるファイル名を意味します。
キーにはAWS IoT SQLの関数を使用することができ、「${関数名}」の形式で指定することで、関数に対応する値を割り当てることができます。
今回の例では、 `${timestamp()}-auth-log-data.json`としていますので、S3格納時にファイル名は「1506675276013-auth-log-data.json」のようにUNIX時間が先頭に付与されたファイル名となります。


- 最後に[ルールの作成]をクリックしてください
- ルール一覧画面に作成したルールが追加されたことをご確認ください


![4-5_4](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-5_4%E6%9E%9A%E7%9B%AE.png)

## 4-6. Kinesis Data Firehose経由でS3バケットにログデータを格納するルールを作成

「顔分析ログデータ」については、Kinesis Data Firehoseを使用して60秒間に送信されてきたデータを１ファイルとして集約した状態でS3に保存します。
データを１ファイルに集約させることで、次ステップで実施するBIツールへのデータロード時間を短縮することが可能です。

今回のハンズオンでは60秒間のデータを１ファイルとしていますが、実際のプロダクションで使用する場合はなるべく大きな単位でファイル集約する方が後続での取り扱いが容易くなると思いますので、ユースケースに応じて調整してください。

- 顔分析ログデータ
 - ルール名：任意の名称（例： `yamadaPutAnalysisLogDataToS3`）
 - 説明： 任意
 - ルールクエリステートメント： `SELECT*FROM 'handson/analysisLogData'`

### 4-6-1. 顔分析ログのルールを追加する

- 「Amazon Kinesis Firehose ストリームにメッセージを送信する」にチェックを付けて[アクションの設定]をクリックしてください
![4-6_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-3.png)

### 4-6-2. [新しいリソースを作成する]をクリックする
![4-6_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-4.png)

### 4-6-3. [Create Delivery Stream]をクリックする
![4-6_3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-5.png)

### 4-6-4. [Delivery stream name]を入力し、「Source」で[Direct PUT or other sources]にチェックする
![4-6_4](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-6.png)

### 4-6-5. [Next]をクリックする
![4-6_5](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-7.png)

### 4-6-6. 何も変更せずに[Next]をクリックする
![4-6_6](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-8.png)

### 4-6-7. 「Destination」で[S3]にチェックを入れる
![4-6_7](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-9.png)

### 4-6-8. 「S3 bucket」で顔分析ログ格納用のS3を選択する
![4-6_8](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-10.png)

### 4-6-9. 以下の設定にしてください
Buffer intervalを60秒にすると、60秒間データを溜め続けた後にS3にデータを出力するようになります。

| 項目       |    値    |
|:-----------------|:------------------:|
| Buffer size             |        5 MB        |
| Buffer interval           |       60 secounds       |
| S3 compression            |        Disabled        |
| S3 encryption               |         Disabled         |

![4-6_9](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-11.png)

### 4-6-10. 「Error logging」は[Enabled]にチェックを入れてください。その後、「I AM role」の[Create new or choose]をクリックし、ロールを作成してください
![4-6_10](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-12.png)
![4-6_10_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-13.png)

### 4-6-11. [Next]をクリックしてください
![4-6_11](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-14.png)

### 4-6-12. 確認画面に遷移されます。内容に問題なければ[Create delivery stream]をクリックしてください
![4-6_12](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-15.png)

- Kinesis Data Firehoseの作成が完了しましたので、IoT Coreのルール作成の画面に戻ってください
- Kinesis Data Firehoseの作成は別タブで開いていますので閉じて、元タブを開いてください

### 4-6-13. 以下の設定を行い、「更新」をクリックしてください
- 先ほど作成したKinesis Firehoseストリームを設定する
- [Separator]に `\n(改行)`を選択する
- ロールを新規に作成し設定する
- 
![4-6_13](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6-16.png)

## 4-7. S3バケットにログデータを格納するルールの動作を確認

ステップ4-3を参考にしながら、ステップ4-5で作成したルールが期待通りの動作をするかテストしましょう。
テストデータは以下に用意しているものをお使いください。

- [認証ログデータ]
  - トピック名： `handson/authLogData`
  - JSONデータ：

```json
{
 "DeviceID": "id001",
	"Datetime": "2019-01-01 00:00:00",
	"AuthenticationResult": true,
	"PictureName": "hoge.png",
	"Person": "piyo"
}
```

- [開閉ログデータ]
  - トピック名： `handson/doorOpenLogData`
  - JSONデータ：

```json
{
	"DeviceID": "id001",
	"Datetime": "2019-01-01 00:00:00",
	"Person": "piyo"
}
```

- [顔分析ログデータ]（60秒間のデータが１ファイルに集約されるため複数回データ送信しましょう）
  - トピック名： `handson/analysisLogData`
  - JSONデータ：

```json
{
	"Datetime": "2019-01-01 00:00:00",
	"AgeRange-Low": 15,
	"AgeRange-High": 20,
	"Gender": "Female",
	"Smile": true,
	"Eyeglasses": false,
	"Sunglasses": false,
	"Beard": false,
	"Mustache": false,
	"EyesOpen": false,
	"MouthOpen": true
}
```

```json
{
	"Datetime": "2019-01-01 00:00:10",
	"AgeRange-Low": 20,
	"AgeRange-High": 24,
	"Gender": "Male",
	"Smile": false,
	"Eyeglasses": false,
	"Sunglasses": true,
	"Beard": false,
	"Mustache": true,
	"EyesOpen": false,
	"MouthOpen": false
}
```

```json
{
	"Datetime": "2019-01-01 00:00:20",
	"AgeRange-Low": 40,
	"AgeRange-High": 45,
	"Gender": "Male",
	"Smile": true,
	"Eyeglasses": false,
	"Sunglasses": true,
	"Beard": true,
	"Mustache": true,
	"EyesOpen": true,
	"MouthOpen": false
}
```
- IoT Coreの「テスト」からテストデータを発行（パブリッシュ）してください
![4-6_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6_1%E6%9E%9A%E7%9B%AE.png)

- AWSコンソールから対象のS3バケットの中身を確認しファイルが作成されていることをご確認ください
![4-6_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-6_2%E6%9E%9A%E7%9B%AE.png)

#### 【注意】 ルールの動作確認が終わったら、テストデータを削除しましょう
このステップでテストとしてパブリッシュしたデータは、ダミーデータです。
本来のデータと混ざり合ってしまうと、ステップ5での分析に影響が出ますので、必ず削除しましょう。

ステップ4-4で作成したS3バケット（例： `sensor_data_table`）の項目一覧から、テストで送信したデータ項目にチェックを入れ、[アクション]から[削除]を行なってください。

## 4-8. IoT Coreのトピックにデータをパブリッシュできる権限を作成

デバイスからIoT Coreのトピックにデータを送信するためには、そのための権限が必要です。
ステップ1-3-2で作成したIAMユーザーに対して、新たに上記の権限ポリシーを追加するのが良いでしょう。


- 下記の順にAWSのコンソールを遷移してください
[IAM Management Console] -> [ユーザー] -> [ステップ1で作成したユーザー] -> [アクセス権限] -> [インラインポリシーの追加]
![4-7_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-7_1%E6%9E%9A%E7%9B%AE.png)


- 今回は、下記のJSON形式のインラインポリシーをそのまま利用します。
[JSON]のタブを開き、下記をコピー&ペーストしてください。

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "iot:Connect",
                "iot:Publish"
            ],
            "Resource": [
                "arn:aws:iot:ap-northeast-1:*:topic/handson/*",
                "arn:aws:iot:*:*:client/*"
            ]
        }
    ]
}
```

- ポリシーの作成を完了し、IAMユーザーに今回作成したポリシーが新たに追加されていることを確認しましょう。
![4-7_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step4/4-7_2%E6%9E%9A%E7%9B%AE.png)


## 4-9. デバイスからIoT Coreにデータをパブリッシュする

デバイス内から、各種ログデータを、前のステップで作成した対応するトピックに送信する処理を行うPythonプログラムを作成します。

今回の通信方式は、IoTでよく使われているMQTT通信ではなく、HTTP通信で行います。
MQTT通信を使用する場合は、クラウド側で証明書を発行し、デバイス側のストレージに保管しSDKから証明書を指定させる必要があります。

AWSとMQTT通信でデータの送受信を試してみたい場合は、弊社の別の[IoTハンズオン記事](https://iot.kyoto/integration_case/2019/04/13/3739/)をお試しください。

#### ＜MQTTとは？＞

MQTTはHTTPのようにヘッダサイズが大きくない為、軽量に送信することができるプロトコルです。
MQTTはパブリッシュ（Publish）・サブスクライブ（Subscribe）、そしてブローカー（Broker）という独自の概念を持ちます。
データを送信することを「パブリッシュする」、特定のトピックに届くデータを待ち受けることを「サブスクライブする」と言います。
パブリッシュする場合、トピックを指定し、ブローカー（今回はIoT Core）にメッセージを渡します。
ブローカーはトピックをサブスクライブしている（待ち受けている）Actにメッセージを受け渡します。
この受け渡しはQoSによって保証されています。

#### ＜QoSとは？＞

QoSは通信の品質のことです。このQoSのレベルを指定することで、どのように通信を保証するかを決めることができます。
このレベルは3段階あり、それぞれ下記の通りです。

- QoS0: メッセージを最大で1回届ける（再送しない）
- QoS1: メッセージを最低1回届ける（到達確認が取れない場合も再送する）
- QoS2: メッセージを必ず1回届ける（到達確認が取れた後、更にそれが正しいかの確認をとる）

AWS IoT Coreでは、QoS2はサポートしていません。
QOS0あるいはQOS1を使用してください。

このようにAWS IoT Coreでは、QoS2をサポートしていないため複数回同じデータが届くことを考慮した設計にする必要があることをご留意ください。
センシティブなデータを取り扱う場合は、必ず１回しか処理されないように別途管理して制御する必要があります。

### 4-9-1. ログデータをIoT Coreのトピックにパブリッシュするプログラムを作成する

ログデータをIoT CoreのトピックにpublishするPythonプログラムをコーディングします。
コードのわかりやすさのため、ログデータごとにPythonプログラムを分けて作成する想定でご説明します。

以下にプログラムに最低限必要な要素を挙げています。注意点もありますのでご確認ください。

サンプルプログラムは[こちら](https://github.com/IoTkyoto/iot-handson-zybo-and-aws/tree/master/step4)にあります。
各 `pub_xxx_log_data.py`の `xxx`が対応するログデータとなっているものをご使用ください。

| スクリプト名 | 説明 | パラメータ |
| ---|---|---|
| pub_analysis_log_data.py | 顔分析ログデータ送信スクリプト | 送信対象データ(JSON形式) |
| pub_auth_log_data.py | 認証ログデータ送信スクリプト | 送信対象データ(JSON形式) |
| pub_door_open_log_data.py | ドア開閉ログデータ送信スクリプト | ドアオープン時の対象者(String) |
| pub_sensor_data.py | センサーデータ送信スクリプト | センサー値(数値) |

- APIから受け取ったデータを渡す方法について
    - 認証ログデータと顔分析ログデータは、それぞれステップ2とステップ3の最後で加工したデータを用います。
    - 加工データの受け渡し方法として、認証ログデータについては、ステップ2-4-1で作成したPythonプログラムに、顔分析ログデータは、ステップ3-4で作成したPythonプログラムに今回作成するプログラムを `import`し、プログラム内で引数を渡しましょう。
    - センサーデータと開閉ログデータについては、自動ドア制御システム側からPythonスクリプトにパラメータを設定し呼び出すことを想定しています。

#### 作成プログラムの解説

- import一覧

    ```python:pub_xxx_log_data.py
    import sys
    import json
    import boto3
    ```
- boto3 client `iot-data`のメソッド `publish`を使用する
   - こちらのドキュメントを参考に実装してください：
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot-data.html#IoTDataPlane.Client.publish
    - `topic`パラメータには、ステップ4-2や4-5でIoT Coreのルールを作成する際に指定したトピック名を文字列として渡します
    - `qos`パラメータには、既出の説明を参考に、 `0`・ `1`のいずれかの数値レベルを指定します
    - `payload`パラメータでは、トピックに送信したいデータを渡します

```python:pub_xxx_log_data.py
        import boto3
        iot_data = boto3.client('iot-data')
        response = iot_data.publish(
                topic='handson/sensorLogData',
                qos = 1,
                payload = sensor_data
        )
```

- 「ドア開閉ログデータ」「センサーデータ」のデバイス識別子、日時
    - どのデバイスからのデータかを識別するための「DeviceId」は「id001」の固定値設定としています
        - プロダクションではデバイスごとに別のID管理を行う必要があります
    - データ日時はPythonスクリプト側で呼び出された日時を設定しています
        - データ日時はグローバル考慮のためUTCで取得しています
        - 表示する側でロケールに合わせて変換が必要です

```python:pub_xxx_log_data.py
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        timestamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        sensor_data_json = {
                                "DeviceID": "id001",
                                "Datetime": timestamp,
                                "Value": self.arg_sensor_data
                            }
        return json.dumps(sensor_data_json)
```

### 4-9-2. 実際に呼び出してみましょう

#### 顔認証・顔分析結果ログのアップロード

- ステップ2-5-6で作成したプログラム「`execute_authentication_api.py`」の28行目、81行目〜83行目と113行目〜114行目のコメントアウトを外しましょう。

```python:execute_authentication_api.py

# step4で作成するログ送信用プログラムのパス
PUB_AUTH_LOG_PATH = '../step4/pub_auth_log_data.py' 

・・・（省略）・・・

def call_pub_auth_log_data(self, format_data):
     for data in format_data:
          subprocess.call(["python3", PUB_AUTH_LOG_PATH, json.dumps(data)])

・・・（省略）・・・

# step4の関数を呼び出す処理
if format_data != []:
   self.call_pub_auth_log_data(format_data)

```

- ステップ3-7で作成したプログラム「`execute_analysis_api.py`」の29行目、72行目〜74行目と96行目〜97行目のコメントアウトを外しましょう。

```python:execute_analysis_api.py

# step4で作成するログ送信用プログラムのパス
PUB_ANALYSIS_LOG_PATH = '../step4/pub_analysis_log_data.py'

・・・（省略）・・・

def call_pub_analysis_log_data(self, format_data):
     for data in format_data:
          subprocess.call(["python3", PUB_ANALYSIS_LOG_PATH, json.dumps(data)])

・・・（省略）・・・

# step4の関数を呼び出す処理
if format_data != []:
     self.call_pub_analysis_log_data(format_data)

```

- 画像のアップロードから顔認証・顔分析を行い結果ログのアップロードまでの一連御処理を実行しましょう

```shell:実行結果
$ python3 upload_target_image.py picture/image01.jpg yamada-target-images-bucket
[succeeded!] upload file name: image01_20190819153823.jpg
{'ResponseMetadata': {'RequestId': 'xxxxxx-xxxx-xxxx-xxxx-xxxxxx', 'HTTPStatusCode': 200, 
'HTTPHeaders': {'content-type': 'application/json', 'content-length': '65', 'date': 'Mon, 19 Aug 2019 06:38:27 GMT', 
'x-amzn-requestid': 'xxxxxx-xxxx-xxxx-xxxx-xxxxxx', 'connection': 'keep-alive'}, 'RetryAttempts': 0}}
・・・（省略）・・・
```

- 渡したデータが、作成したS3バケットに格納されていたら成功です。


#### センサーデータのアップロード

- センサーで取得した数値をパラメータとして指定し、定期的にPythonを呼び出しましょう
- プログラム：pub_sensor_data.py
    - パラメータ：センサー数値

```shell:センサーデータアップロード実行
$ python3 pub_sensor_data.py 13.2
```
- 渡したデータが、作成したDynamoDBテーブルに格納されていれば成功です

#### ドア開閉ログデータのアップロード

- ドアをオープンしたタイミングで呼び出すことでログを記録します
- プログラム：pub_door_open_log_data.py
    - パラメータ：ドアオープン時の対象者（誰に対してドアをオープンしたか）

```shell:ドアオープンログアップロード実行
$ python3 pub_door_open_log_data.py Taro_Yamada
```
- 渡したデータが、作成したS3バケットに格納されていたら成功です。


---

### ★データが格納されていなかった場合
  
ステップ4-3で使用した「テスト」の「サブスクリプション」画面にて、以下を行ってください。

- 「トピックのサブスクリプション」の入力フォームに `#`と入力してください
 `#`はワイルドカードを意味し、全てのトピックを受け付けます。

- 「トピックへのサブスクライブ」をクリックしてください
全てのトピック宛のデータが表示されます。
    
#### データが表示されない場合

- ステップ4-6-1で作成したPythonプログラムによってデータを送信しているにも関わらず、データが表示されない場合

	- 通信状態に問題はありませんか？
	- ステップ4-5でポリシーをアタッチしたIAMユーザーを利用していますか？
	- ステップ4-5でアタッチしたポリシーは正しいですか？
	- トピック名は正しいですか？
	- リージョンは正しいですか？

- データは到達しているが、DynamoDBやS3にデータが格納されない場合

	- ルールの設定は正しいですか？
	- ルールにアタッチされているIAMロールに問題はありませんか？
