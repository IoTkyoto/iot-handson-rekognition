
# ステップ5. ログデータの可視化を行う（スマートフォンとAWSサービスを用いた画像認識サービスの構築する）

*当コンテンツは、エッジデバイスとしてスマートフォン、クラウドサービスとしてAWSを利用し、エッジデバイスとクラウド間とのデータ連携とAWSサービスを利用した画像認識を体験し、IoT/画像認識システムの基礎的な技術の習得を目指す方向けのハンズオン(体験学習)コンテンツ「[スマートフォンとAWSサービスを用いた画像認識サービスの構築する](https://iotkyoto.github.io/iot-handson-rekognition)」の一部です。*

# ステップ5. ログデータの可視化を行う

![ステップ5アーキテクチャ図](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/architecture_step5.png)

最後に、今までのステップで収集しクラウドに保存したデータを可視化します。
今回のハンズオンでは以下の方法でデータ可視化を行います。

- **利用者の状況分析や履歴データの可視化**
    AWSが提供している高速なBIサービス「**Amazon QuickSight**（以下、QuickSight）」を使用します。

IoTセンサーの値などの定期的に送信される時系列数値データを可視化する場合は、弊社で開発・運用している「[IoT.kyoto VIS](https://iot.kyoto/)」を使用することも可能です。

### ＜IoT.kyoto VISとは？＞

Amazon DynamoDBに保存したストリームデータからリアルタイムでグラフを描画することができる、Webアプリケーションです。Webブラウザを用意するだけで、DynamoDBの時系列数値データを折れ線グラフ形式で表示することができ、閾値を設けたアラートの設定や期間を指定しての過去データの表示も可能です。
詳細は[IoT.kyotoのホームページ](https://iot.kyoto)をご確認ください。

## 5-1. Amazon QuickSightで利用データの分析・可視化

### 目的
- デバイス側から収集したログデータを可視化し分析する
- AWSのBIサービスの使用方法を学ぶ
- AWSのS3上に蓄積されたテキストデータの分析手法を知る

### 概要
- S3に蓄積されたログデータをBIツールで分析し表示する
- セミナーではサンプルとして以下の可視化を行う
	- 顔分析対象者の性別の割合（Rekognitionの顔分析の結果）の円グラフを表示

*性別割合のみ可視化を実践し、その他のものは時間があればチャレンジしてください*

---

**当章では、JAWS DAYS 2017のIoTハンズオン向けに作成したコンテンツの後編を流用して説明を行います。**

[RaspberryPi + Athena + Quicksightで可視化する＜前編＞](https://qiita.com/Ichiro_Tsuji/items/d366203c3621e6c15def)
- RasberryPiに接続した温度センサーの値をAmazon Kinesis Firehose経由でAmazon S3にJSON形式でデータを蓄積する  

[RaspberryPi + Athena + Quicksightで可視化する＜後編＞](https://qiita.com/ha_ru_ma_ki/items/ee77b3755ef50181bba4)
- S3に蓄積されたデータに対しAmazon Athenaでクエリを実行しデータソースとしてAmazon QuickSightで表示する

---

### ＜Amazon Athenaとは？＞
Amazon S3内のデータを標準SQLを使って分析できるクエリサービスです。
フルマネージドでサーバーレスなサービスなため、セットアップや管理は不要です。
使い方は簡単で、S3にあるデータを指定して、スキーマを定義し、組み込まれているクエリエディタを使ってクエリを開始できます。
指定するデータは、CSV、JSON、Apacheログなどのさまざまなデータフォーマットを扱う事ができます。
また、QuickSightと統合する事で簡単に可視化する事ができます。

- GZIP等の圧縮ファイルも読み込める
- JDBC経由でのアクセスも可能
- 検索した結果がS3に保存される
- [実行したクエリに対して課金](https://aws.amazon.com/jp/athena/pricing/)

詳細は[AWS公式ガイド](https://aws.amazon.com/jp/athena/)をご確認ください。

![Athenaイメージ画面](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-athena.png)

### ＜Amazon QuickSightとは？＞
AWSが提供するフルマネージドで高速なBIサービスです。
さまざまなデータソースに接続してデータをインポートすることが出来ます。
また、インメモリ処理に最適化されたデータベースである「**SPICE**」（超高速、パラレル、インメモリ、計算エンジン）にデータをインポートする事で、高速な分析が可能です。
作成したグラフはモバイルからの閲覧にも対応しています。

- さまざまなデータソースに対応
  - Salesforce、Twitter、GithubなどのSaaSアプリケーション
  - MySQL、Postgre、SQL Serverなどのサードパーティーのデータベース
  - Redshift、Athena、S3、RDS、Auroraなどのネイティブの AWS のサービス
  - Excel、CSV、JSON、Prestoといったさまざまな形式のファイル
- [利用するアカウントの有効セッション数やSPICEのデータ容量で課金](https://quicksight.aws/pricing/)
- 60日間の試用期間、無料枠もある（1ユーザー、SPICEは1GBまで）
- データの日付フィードの最小粒度は分単位

詳細は[AWS公式ガイド](https://aws.amazon.com/jp/quicksight/)をご確認ください。

### ＜SPICEエンジンとは？＞
- Super-fast, Parallel, In-memory Calculation Engine（超高速で並列稼働するインメモリ計算エンジン）
- AWSがQuickSight用に開発した高速なインメモリ計算エンジン
- SPICEはデータを自動レプリケートして高可用性を確保するため、数千人規模のユーザーが同時に、高速でインタラクティブに分析することが可能
- データをSPICEにインポートすることで、データに対して直接クエリを実行するのではなく、メモリ上のデータにアクセスし高速に分析を行える
- ユーザ毎にデフォルトで１０GBのSPICE容量が提供される（無償利用枠の場合はユーザあたり１GBの容量）
- 通常の利用時は、定期的にデータの自動取込を行い、データのリフレッシュを行う

![QuickSightイメージ画面](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-quicksight_.png)

## 5-1. Amazon Athenaを設定する

顔分析ログデータを利用する場合の手順を説明します。
ステップ3で取得した顔分析ログデータをAthenaに読み込ませましょう。

### 5-1-1. Athenaのコンソール画面を開く
  
  - サービスから「Athena」を選択する
  - リージョンが「東京」となっていること
  - チュートリアルが表示された場合は閉じる

### 5-1-2. データベースとテーブルを作成する

クエリエディタ画面で「テーブルの作成」をクリックし「from S3 bucket data」を選択します。

![5-1-2.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-1-2.png)

### 5-1-3. 「名前と場所」を設定する

以下の通り、作成するデータベースとテーブル名、読み込み対象のS3バケットを指定しましょう。 
  
  - データベース： 新しいデータベースを作成
  - データベース名： 任意の名前（例： `20190823_seminar`）
  - テーブル名： 任意の名前（例： `analysislogdata`）
  - 入力データセットの場所： 対象データが格納されているS3バケットのARN
  　　　　　　　　　　　（例： `s3://yamada-analysis-log-data/`）
  - [次へ]進む

![5-1-3.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-1-3.png)

### 5-1-4. 「データ形式」を設定する

読み込むデータの形式(Apache Web ログ、CSV、TSVなど)を選択します。以下の通り進めてください。

  - データ形式： `JSON`
  - [次へ]進む

![5-1-4.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-1-4.png)

### 5-1-5. 「列」を設定する

こちらで読み込み対象のデータのスキーマ情報を設定します。

|列名  |列のタイプ  |
|---|---|
| datetime | timestamp |
| agerange-low | smallint |
| agerange-high | smallint |
| gender | string |
| smile | boolean |
| eyeglasses | boolean |
| sunglasses | boolean |
| beard | boolean |
| mustache | boolean |
| eyesopen | boolean |
| mouthopen | boolean |

[列の一括追加]をクリックし、以下のコードを貼り付けて、[の追加]ボタンをクリックしてください

`datetime timestamp, agerange-low smallint, agerange-high smallint, gender string, smile boolean, eyeglasses boolean, sunglasses boolean, beard boolean, mustache boolean, eyesopen boolean, mouthopen boolean`

![5-1-5_1.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-1-5_1.png)

  - [次へ]進む
![5-1-5_2.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-1-5_2.png)

### 5-1-6. 「パーティション」を設定する

データを[パーティション分割](https://docs.aws.amazon.com/ja_jp/athena/latest/ug/partitions.html)することで、各クエリでスキャンするデータの量を制限し、パフォーマンスの向上とコストの削減を達成できます。
今回はパーティション設定は行いません。

- 何も設定せずに「テーブルの作成」クリック
![5-1-6.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-1-6.png)

### 5-1-7. テーブル作成結果を確認する

- 結果欄に「クエリは成功しました。」と表示されていることを確認
- 左側にデータベース・テーブルが存在していることを確認

![5-1-7.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-1-7.png)

### 5-1-8. クエリを実行してみる

- クエリ欄の内容を以下に変更し「クエリの実行」をクリックし、結果欄にデータが表示されることを確認する

```
SELECT * FROM "20190823_seminar"."analysislogdata" limit 10;
```

![5-1-8.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-1-8.png)

**Athenaでは、このようにS3バケットに格納しているJSONファイルに対してクエリを実行し結果を取得することができます。**


## 5-2. Amazon QuickSightのアカウントを開設する

つづいて、QuickSightを使用するためにアカウントを作成しましょう。

### 5-2-1. QuickSightのコンソール画面を開く

- サービスから「QuickSight」を選択する
 - リージョンが「東京」となっていること
 - 別タブでQuickSightが起動する

### 5-2-2. QuickSightのアカウントを作成する

はじめてQuickSightを起動した場合は、以下のサインアップ画面が表示されます。

- [Sign up for QuickSight]をクリック
![5-2-2.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-2-2.png)

### 5-2-3. QuickSightアカウントの種別を選択する

- 「スタンダード版」を選択し[続行]をクリック
![5-2-3.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-2-3.png)
  
### 5-2-4. アカウント作成に必要な情報を入力する
- QuickSightリージョン： `Asia Pacific（Tokyo）`
- QuickSightアカウント名： 任意のアカウント名（例： `yamada`）
- 通知のEメールアドレス： 受信可能なメールアドレス（例： `taro@yamada.co.jp`）
- Enable autodiscovery...： チェックON
- Amazon Athena： チェックON
- 上記以外： チェックOFF
- [完了]をクリック

![5-2-4.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-2-4.png)

### 5-2-5. QuickSightを開く

「おめでとうございます。Amazon QuickSight にサインアップしました。」のメッセージが表示されればアカウントは正常に作成されています

- [Amazon QuickSightに移動する]をクリック
![5-2-5.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-2-5.png)

### 5-2-6. QuickSightへようこそ

QuickSightのサイトが立ち上がり、チュートリアルが表示されます。
![5-2-6.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-2-6.png)

## 5-3. QuickSightにS3バケットへのアクセス権限を付与する

QuickSightにデータソースを指定する前に、読み込み対象のS3バケットへの権限を付与しましょう。

### 5-3-1. QuickSightの設定画面を開く

- メニューの右上にあるアカウントアイコンをクリックし[QuickSightの管理]をクリック
![5-3-1.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-3-1.png)

### 5-3-2. セキュリティとアクセス権限画面を開く

- 設定画面の左メニューから[セキュリティとアクセス権限]をクリック
- セキュリティとアクセス権限の[追加または削除する]をクリック

![5-3-2.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-3-2.png)

### 5-3-3. 接続先のS3バケットを追加する

- 接続された製品とサービスの「Amazon S3」にチェックをつける
- ポップアップ画面で顔分析ログデータを保存しているS3バケットにチェックを付与する
- [バケットの選択]をクリック
- [更新]をクリック

![5-3-3.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-3-3.png)

**注意：S3バケットへの権限を付与しない状態で、データセットを作成するとPermissionエラーが発生します。**

## 5-4. QuickSightのデータソースを作成する

ステップ5−1で作成したAthenaデータからデータソースを作成し、SPICEに読み込ませましょう。

### 5-4-1. データソース管理画面を開く

- QuickSightのトップページの右上の[データの管理]をクリック
![5-4-1.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-4-1.png)

### 5-4-2. 新しいデータセットを作成する

- データの管理画面の[新しいデータセット]をクリック

![5-4-2.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-4-2.png)

### 5-4-3. データセットとしてAthenaを追加する

- データセットの作成の[Athena]をクリック
- ポップアップ画面でデータセット作成に必要な項目を入力する
- データソース名： 任意の名前（例： `analysisLogData`）
- [データソースを作成]をクリック

![5-4-3.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-4-3.png)

### 5-4-4. Athenaのデータベース・テーブルを選択する
- データベース： ステップ5−1で作成したデータベースを選択
- テーブル： ステップ5−1で作成したテーブルを選択
- [選択]をクリック

![5-4-4.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-4-4.png)

### 5-4-5. Athenaのデータベース・テーブルを選択する
- 「迅速な分析のためにSPICEへインポート」にチェックをつける
- [Visualize]をクリック

![5-4-5.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-4-5.png)

### 5-4-6. データのインポートを確認する

- インポートが完了するまで、しばらく待つ
- Analysis画面の右上に「インポートの完了：100% が成功しました」と表示されることを確認

![5-4-6.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-4-6.png)

## 5-5. QuickSightでデータの可視化を行う

さいごに、QuickSightで画像の人物の性別割合を例として可視化してみましょう。

### 5-5-1. 可視化項目を選択する

- 左側のフィールドリストから「gender」をクリックする
- 右側のグラフ部分が自動的にデータ形式を判断し、横棒グラフ形式でカウントを表示してくれます

![5-5-1.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-5-1.png)

**このようにQuickSightでは選択したデータ型によって自動的に適したグラフ形式で描画してくれます。**

### 5-5-2. グラフ形式を円グラフに変更する

- 左下のビジュアルタイプの「円グラフ」をクリックする
![5-5-2.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-5-2.png)

### 5-5-3. グラフの表示内容をカスタマイズする

- グラフの右上の「下矢印」をクリックする
- [ビジュアルのフォーマット]をクリックする

![5-5-3_1.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-5-3_1.png)

- 左側に表示された項目の設定を変更することで、凡例の表示やラベルとしてメトリクスの表示が可能
- またグラフの円部分をクリックすることで色の変更などグラフ表示内容の変更も可能

![5-5-3_2.png](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step5/5-5-3_2.png)

### 5-5-4. QuickSightをもっと体験してみましょう

JAWS DAYSの[ハンズオン記事](https://qiita.com/ha_ru_ma_ki/items/ee77b3755ef50181bba4)には、SPICEのデータのリフレッシュの方法や、データを自動更新する方法や、計算フィールドの設定方法などが記載されているので、これを参考にしてQuickSightをもっと体験してみましょう。
時間があまった方は、S3に格納した他のデータ「認証ログデータ」「自動ドア開閉ログデータ」の可視化にもチャレンジしてみてください。


---

### おつかれさまです！

以上でハンズオンコンテンツ「 **スマートフォンとAWSサービスを用いた画像認識サービスの構築する** 」は終了です。[アジェンダ](https://iot.kyoto)に戻り、「さいごに」をご確認ください。
