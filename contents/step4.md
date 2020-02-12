# ステップ4. ログデータをクラウドにアップロードする（スマートフォンとAWSサービスを用いた画像認識サービスの構築する）

*当コンテンツは、エッジデバイスとしてスマートフォン、クラウドサービスとしてAWSを利用し、エッジデバイスとクラウド間とのデータ連携とAWSサービスを利用した画像認識を体験し、IoT/画像認識システムの基礎的な技術の習得を目指す方向けのハンズオン(体験学習)コンテンツ「[スマートフォンとAWSサービスを用いた画像認識サービスの構築する](https://qiita.com/kyoso_bizdev/private/e5c252f08de019ab8a1b)」の一部です。*

# ステップ4. ログデータをクラウドにアップロードする

![ステップ4アーキテクチャ図](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/architecture_step4.png)

ステップ4では、前回までのステップでWeb APIから受け取った顔画像分析結果データを、クラウドに送信し蓄積する仕組みを構築します。
データを格納することで、次のステップでデータの可視化が行えるようになります。

AWS IoT Coreで作成したトピックに対して、デバイスからHTTPアクセスで各種データを送信します。
次にIoT Coreでルールを作成します。
このルールは待ち受けているトピックで受信したデータをS3に格納するように設定します。

顔画像分析ログデータについては、各所から集められる大量のストリーミングログデータを欠損なく扱うユースケースとして、[Amazon Kinesis Data Firehose](https://aws.amazon.com/jp/kinesis/data-firehose/)経由でデータの保存を行います。

今回の手順では、先にデータの格納先を準備し、次にルールを作成、最後にデバイスからログデータを送信するプログラムを作成します。

**注意：今回のIoT通信の方法について**
今回のハンズオンではIoTで通常よく使われるMQTT通信ではなく、HTTP通信を利用しています。
MQTT通信を利用する場合は、端末ごとの認証や証明書の準備が必要なため、HTTP通信を利用し簡素化しています。
また、デバイス側でトピックのサブスクライブ（データ受信）は行わず、トピックへのパブリッシュ（データ送信）のみ実施しています。

---

### 目的

- デバイス側のデータをクラウドに送信する手法を学ぶ
- AWSでのデータ蓄積方法を学ぶ
- AWSでのデータ収集環境を構築する

### 概要

- デバイス側で発生したログ情報をクラウドにアップロードする
- AWS IoT Coreを使用する（HTTPアクセス）
- 以下のログデータを送信する
	- 顔画像分析ログデータ -> Kinesis Data Firehose経由 -> S3バケットに格納

---

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

## 4-1. 顔画像分析ログデータを格納するためのS3バケットを作成

まずは、顔画像分析ログデータを格納するためのS3バケットを作成します。

- 下記の設定を見ながら各種用途別に作成してください

  - **顔画像分析ログデータ格納用バケット**
    - バケット名：全世界で一意となる任意の名称(例: `yamada-analysis-log-data`)
    - 設定： デフォルト(非公開設定)

- S3バケットの作成方法が分からない場合は、ステップ１をご確認ください

## 4-2. Kinesis Data Firehose経由でS3バケットにログデータを格納するルールを作成

「顔画像分析ログデータ」は、Kinesis Data Firehoseを使用して60秒間に送信されてきたデータを１ファイルとして集約した状態でS3に保存します。
データを１ファイルに集約させることで、次ステップで実施するBIツールへのデータロード時間を短縮することが可能です。

今回のハンズオンでは60秒間のデータを１ファイルとしていますが、実際のプロダクションで使用する場合はなるべく大きな単位でファイル集約する方が後続での取り扱いが容易くなると思いますので、ユースケースに応じて調整してください。

- 顔分析ログデータ
 - ルール名：任意の名称（例： `yamadaPutAnalysisLogDataToS3`）
 - 説明： 任意
 - ルールクエリステートメント： `SELECT * FROM 'handson/analysisLogData'`

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

今回使用するクエリは「`SELECT*FROM 'handson/analysisLogData'`」ですので、「handson/analysisLogData」トピックのメッセージの全文にアクションを適用する意味となります。

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

### 4-2-1. アクションを追加する

- WSのコンソール画面で**IoT Core**を検索・選択し、左側メニューの[ACT]をクリックしてください

- ルール一覧画面の右上の[作成]をクリックしてください
![4-2-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-1_1.png)

- 「名前」に任意の名前を入力してください
（例： `yamadaPutAnalysisLogDataToS3`）
![4-2-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-1_2.png)

- 「ルールクエリステートメント」に以下のクエリ文を入力してください
```sql
SELECT * FROM 'handson/analysisLogData'
```
![4-2-1_3](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-1_3.png)

- [アクションの追加]をクリックしてください
![4-2-1_4](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-1_4.png)

### 4-2-2. KinesisFirehoseの設定を行う

- アクションの設定画面で「Amazon Kinesis Firehose ストリームにメッセージを送信する」にチェックを付けて[アクションの設定]をクリックしてください
![4-2-2_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_1.png)

- [新しいリソースを作成する]をクリックする
![4-2-2_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_2.png)

- [Create Delivery Stream]をクリックする
![4-2-2_3](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_3.png)

- [Delivery stream name]を入力し、「Source」で[Direct PUT or other sources]にチェックする
![4-2-2_4](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_4.png)

- [Next]をクリックする
![4-2-2_5](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_5.png)

- 何も変更せずに[Next]をクリックする
![4-2-2_6](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_6.png)

- 「Destination」で[S3]にチェックを入れる
![4-2-2_7](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_7.png)

- 「S3 bucket」で顔画像分析ログ格納用のS3を選択する
![4-2-2_8](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_8.png)

- 設定画面の項目を以下の通り入力する
Buffer intervalを60秒にすると、60秒間データを溜め続けた後にS3にデータを出力するようになります。

| 項目       |    値    |
|:-----------------|:------------------:|
| Buffer size             |        5 MB        |
| Buffer interval           |       60 secounds       |
| S3 compression            |        Disabled        |
| S3 encryption               |         Disabled         |

![4-2-2_9](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_9.png)

- 「Error logging」は[Enabled]にチェックを入れてください。
その後、「I AM role」の[Create new or choose]をクリックし、ロールを作成してください
![4-2-2_10](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_10.png)
![4-2-2_11](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_11.png)

- [Next]をクリックしてください
![4-2-2_12](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_12.png)

- 確認画面に遷移されます。内容に問題なければ[Create delivery stream]をクリックしてください
![4-2-2_13](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_13.png)

- Kinesis Data Firehoseの作成が完了しましたので、IoT Coreのルール作成の画面に戻ってください
（Kinesis Data Firehoseの作成は別タブで開いていますので閉じて、元タブを開いてください）

- アクションの設定画面で以下の設定を行い、「更新」をクリックしてください
  - 先ほど作成したKinesis Firehoseストリームを設定する
  - [Separator]に `\n(改行)`を選択する
  - ロールを新規に作成し設定する
![4-2-2_14](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-2-2_14.png)

## 4-3. ルールの動作を確認する

ステップ4-2で作成したルールが期待通りの動作をするか、AWSのコンソールからトピックを指定しメッセージを発行(パブリッシュ)してテストしてみましょう。

- IoT Coreコンソールの左メニューの[テスト]をクリックしてください
![4-3_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-3_1.png)

- 画面下部の[発行]エリアに以下の内容を入力してください

  - テストデータ
    - [センサーデータ]トピック名： `handson/analysisLogData`
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

- [トピックに発行]をクリックしてください
![4-3_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-3_2.png)

- 60秒間のデータが１ファイルに集約されるため複数回データ送信しましょう

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

- AWSコンソールから対象のS3バケットの中身を確認しファイルが作成されていることをご確認ください
![4-3_3](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-3_3.png)

#### 【注意】 ルールの動作確認が終わったら、テストデータを削除しましょう
このステップでテストとしてパブリッシュしたデータは、ダミーデータです。
本来のデータと混ざり合ってしまうと、ステップ5での分析に影響が出ますので、必ず削除しましょう。

ステップ4-1で作成したS3バケット（例： `yamada-analysis-log-data`）の項目一覧から、テストで送信したデータ項目にチェックを入れ、[アクション]から[削除]を行なってください。

## 4-4. IoT Coreのトピックにデータをパブリッシュできる権限を作成

デバイスからIoT Coreのトピックにデータを送信するためには、そのための権限が必要です。
ステップ1-3,1-4のIAMユーザー・ポリシーの作成方法を参考にして、新たに特定トピックにデータ送信するためだけの権限を持ったIAMユーザーを作成しましょう。

### 4-4-1. トピックへ送信可能なポリシーの作成

- AWSのコンソール画面で「IAM」を検索・選択し[ポリシー] -> [ポリシーの作成]をクリックしてください

- 今回は1-3で行ったビジュアルエディターによるポリシー設定ではなく、JSON形式でのポリシー設定行います
[JSON]のタブを開き、下記コードをペーストし、「`ポリシーの確認`」をクリックしてください
![4-4-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-4-1_1.png)

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

**上記設定内容は、IoT Coreへの接続とトピック「handson/*」への送信(パブリッシュ)のみを許可するポリシーとなります**

- ポリシーの作成に必要な情報を入力・確認し、「`ポリシーの作成`」をクリックしてください
    - 名前：任意の名称（例：yamada_iot_publish_policy）
    - 説明：任意（例：Policy for IoT Core Topic Publish on Mobile）
    - 概要：[IoT]をクリックし以下の画像の通りであること
![4-4-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-4-1_2.png)

### 4-4-2. トピックへ送信可能なIAMユーザーの作成

トピックへデータ送信するためのIAMユーザーを作成し、ステップ4-4-1で作成したポリシーを関連付けします。

- IAM画面のサイドメニュー欄から「`ユーザー`」をクリックし、ユーザ一覧上部の「`ユーザーを追加`」をクリックしてください

- 以下の情報を入力し、「`次のステップ:アクセス権限`」をクリックしてください
    - ユーザー名：任意の名称（例：yamada_iot_publish_user）
    - プログラムによるアクセス：チェック
    - AWSマネジメントコンソールへのアクセス：チェックなし
![4-4-2_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-4-2_1.png)
*このステップで作成するユーザはデバイスからAWS SDK経由のプログラムからアクセスするためのユーザとなりますので、AWSコンソールへのログインは不要としプログラムによるアクセスのみ有効としましょう。*

- 設定するポリシーを指定し、「`次のステップ:タグ`」をクリックしてください
    - アクセス許可の設定欄の「既存のポリシーを直接アタッチ」をクリック
    - ステップ4-4-1で作成したポリシーを検索しチェックを付与
    （例：yamada_iot_publish_policy）
![4-4-2_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-4-2_2.png)

- 今回のケースではタグを使用しないため、何も入力せずに「`次のステップ:確認`」をクリックしてください
![4-4-2_3](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-4-2_3.png)

- 確認画面で表示されている内容に問題がなければ、「`ユーザーの作成`」をクリックしてください
![4-4-2_4](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-4-2_4.png)

- AWSにアクセスするための認証（クレデンシャル）情報として、アクセスキーとシークレットアクセスキーが生成されます
次のステップで利用しますのでダウンロードしておきましょう
![4-4-2_5](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step4/4-4-2_5.png)

## 4-5. デバイスからIoT Coreにデータをパブリッシュする

デバイスから顔画像分析結果ログデータをトピックに送信する処理を行います。

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

### 4-5-1. ログデータをIoT Coreのトピックにパブリッシュするプログラムを作成する

ログデータをIoT CoreのトピックにpublishするJavaScriptプログラムをコーディングします。
今回は、プログラム部分については事前に準備済みですのでコードの解説を行います。

以下にプログラムに最低限必要な要素を挙げています。
注意点もありますのでご確認ください。

サンプルプログラムは[こちら](https://github.com/IoTkyoto/iot-handson-zybo-and-aws/tree/master/step4)にあります。
各 `pub_xxx_log_data.py`の `xxx`が対応するログデータとなっているものをご使用ください。

| スクリプト名 | 説明 | パラメータ |
| ---|---|---|
| pub_analysis_log_data.py | 顔分析結果ログデータ送信スクリプト | 送信対象データ(JSON形式) |

#### 作成プログラムの解説

- 使用するライブラリ
    AWS SDK for JavaScript
    ```JavaScript
    npm install aws-sdk
    ```

- import一覧
    ```JavaScript
    import AWS from 'aws-sdk';
    ```

- AWS SDKの `IoTData`クラスの `publish`メソッドを使用する
    - こちらのドキュメントを参考に実装してください：
        - https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/IotData.html
        - https://docs.aws.amazon.com/iot/latest/apireference/API_iotdata_Publish.html
    - パラメータ
        - `topic`：ステップ4-2-1でIoT Coreのルールを作成する際に指定したトピック名を文字列として渡します
        - `qos`：既出の説明を参考に、 `0`・ `1`のいずれかの数値レベルを指定します
        - `payload`：トピックに送信したいデータを渡します

    ```JavaScript
    import AWS from 'aws-sdk';
    var iotdata = new AWS.IotData({
        endpoint: this.endpoint,
        apiVersion: '2015-05-28'
    });
    var params = {
        topic: this.topicName, /* required */
        payload: resultJsonData,
        qos: '0'
    };
    iotdata.publish(params, function(err, data) {
        if (err) console.log(err, err.stack); // an error occurred
        else     console.log(data);           // successful response
    });
    ```

### 4-5-2. デバイスに設定情報を登録する



### 4-5-2. デバイスから結果データをIoT Coreのトピックにパブリッシュする

#### ４−5−2−1. 顔認証・顔分析結果ログのアップロード

- 

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
