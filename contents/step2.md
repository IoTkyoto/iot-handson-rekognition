# ステップ2. 顔認証のWeb APIを作成する（スマートフォンとAWSサービスを用いた画像認識サービスの構築する）

*当コンテンツは、エッジデバイスとしてスマートフォン、クラウドサービスとしてAWSを利用し、エッジデバイスとクラウド間とのデータ連携とAWSサービスを利用した画像認識を体験し、IoT/画像認識システムの基礎的な技術の習得を目指す方向けのハンズオン(体験学習)コンテンツ「[スマートフォンとAWSサービスを用いた画像認識サービスの構築する](https://qiita.com/kyoso_bizdev/private/e5c252f08de019ab8a1b)」の一部です。*

# ステップ2. 顔認証のWeb APIを作成する

![ステップ2アーキテクチャ図](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step2/architecture_step2.png)

ステップ2では、前ステップでS3バケットにアップロードされた画像を分析し、「事前登録済みの人物が写っているか、写っている場合は誰かを判定する」機能を持ったWeb APIを作成し、デバイス側からAPIを呼び出す仕組みを構築します。

まずは、「**[Amazon Rekognition（以下、Rekognition）](https://aws.amazon.com/jp/rekognition/)**」を利用して「コレクション」を作成し、認識対象となる顔を登録します。
次に、作成したコレクションを使って顔の認識を行う「**[AWS Lambda（以下、Lambda）](https://aws.amazon.com/jp/lambda/)**」を作成します。
さいごに、作成したLambdaにHTTPでアクセスするために「**[Amazon API Gateway（以下、API Gateway）](https://aws.amazon.com/jp/api-gateway/)**」を作成します。

---

### 目的

- デバイスから外部APIに利用する方法を学ぶ
- JSON形式のファイルの取り扱いを学ぶ
- AWSでのAPI構築方法を学ぶ
- AWSの画像認識機能を知る

### 概要

<!-- TODO: 全体の項目が決まってからこちらに反映する -->

- 顔認証用のWebAPIを作成し、デバイスからWebAPIを利用する
 - APIのリクエスト・レスポンスを取り扱う
 - WebAPIの認証はAPIキーを使う
- 顔認識用のコレクションを作成し、対象者が画像に写っているかどうかの画像認識を行う

---

### ＜Web APIとは？＞

HTTPプロトコルを利用してインターネットを介したアプリケーション間のやりとりを行うためのインターフェースです。
Web APIの代表的な実装方式として、RESTとSOAPが存在しており、今回作成するWeb APIはREST APIとなります。

- REST
  - RESTとはRepresentational State Transferの略称
  - 以下のRESTの思想に従って実装されたAPIをRESTful API（またはREST API）と呼ぶ
    - HTTPのメソッド（命令）でデータ操作種別（CRUD）を表す
    - ステートレス
    - URIで操作対象のリソースを判別可能にする
    - レスポンスとしてXMLもしくはJSONで操作結果を戻す
- SOAP
  - SOAPは、XMLを利用したWebサービス連携プロトコル
  - XMLで記述された「SOAPメッセージ」と呼ばれるデータをやりとりすることで、メッセージを交換する

様々な公開Web APIが提供されていることや、わかりやすいデータのやり取りから、Web APIを利用してモノリシックなシステムをマイクロサービス化することが現在の潮流となっています。


### ＜AWS Lambdaとは？＞

AWS Lambdaは、サーバーをプロビジョニングしたり管理する必要なくコードを実行できるサーバーレスコンピューティングサービスです。これは他のAWSサービスをトリガーとして実行することができ、実際に処理にかかった時間やリクエスト数に対して従量課金されます。Lambda関数はJavaやPythonをはじめとした一般的なプログラミング言語で作成することができます。

- サーバー管理が不要
- 実行時のメモリ量を指定することで、それに比例したCPUパワー/ネットワーク帯域/ディスクIOが割り当てられる
- リクエスト受信の回数に合わせて自動的にスケールする
- コードが実行されている間のコンピューティング時間に対しての[ミリ秒単位の課金](https://aws.amazon.com/jp/lambda/pricing/)
- Java、Go、PowerShell、Node.js、C#、Python、Rubyのコードをサポート
- カスタムランタイムで上記以外の言語の使用も可能(COBOLなど)

より詳しく知りたい場合は[公式サイト](https://aws.amazon.com/jp/lambda/)をご確認ください。

### ＜Amazon API Gatewayとは？＞

Amazon API Gatewayは、開発者があらゆる規模でAPIの公開、保守、モニタリング、セキュリティ保護、運用を簡単に行えるフルマネージドサービスです。
セキュアで信頼性の高いAPIを大規模に稼働させるために、差別化にはつながらない面倒な作業を処理する従量制のサービスです。
AWS、または他のウェブサービス、AWSクラウドに保存されているデータにアクセスするAPIを作成できます。ユースケースとしては、モバイルアプリやWebアプリケーションのバックエンドAPIとして、API GatewayとLambdaを連携させて、サーバレスなREST API環境を構築するケースでよく使われます。

- スケーラブル
    - 最大数十万規模の同時APIコールの受け入れと処理に伴うすべてのタスクを取り扱うことが可能
    - 内部でCloudFrontの仕組みを利用しており、スケーラビリティやアベイラビリティの面でCloudFrontの特徴を享受している
- APIの作成およびデプロイが容易
    - APIのステージング管理が可能
    - Canaryリリースのデプロイが可能
- ステートフル(WebSocket)およびステートレス(REST)なAPIのサポート
- 強力で柔軟性に優れた認証メカニズム
    - IAMポリシー、Lambdaオーソライザー関数やCognitoユーザープールなどでの認証が可能
- APIリクエスト数に応じた安価な[従量課金](https://aws.amazon.com/jp/api-gateway/pricing/)

より詳しく知りたい場合は[公式サイト](https://aws.amazon.com/jp/api-gateway/)をご確認ください。

### ＜APIキー認証とは？＞
API Gatewayがサポートする認証方式の１つで、所定のキー(文字列)をHTTPヘッダ(x-api-keyヘッダ)に含めたリクエストであればアクセスを許可、無ければアクセスを拒否する機能です。APIキーの発行・管理は、API Gateway側で行われます。
また、ユーザごとにAPIキーを発行し、ユーザごとに呼び出し回数に制限をかけるというような使用法も可能です。
ただし、APIキーはヘッダー解析などをされることで漏洩する可能性がありますので、認証の唯一の手段としてAPIキーを使用することはベストプラクティスではありません。
認証機能が必要な場合は、IAMロール、Lambdaオーソライザー、または Amazon Cognitoユーザープールを使用するようにしてください。
https://docs.aws.amazon.com/ja_jp/apigateway/latest/developerguide/api-gateway-api-usage-plans.html


## 2-1. Lambdaを作成

ここでは、スマホからAPI Gatewayを通して受け取った顔画像が、ステップ1で作成したRekognitionのコレクションに登録済みの人物とマッチするかどうか、マッチする場合は誰であるかリターン値として返すLambdaファンクションを作成します。

### 2-1-1. Lambda関数を作成する

- AWSのコンソール画面で、「Lambda」を検索・選択し、[関数の作成]をクリックします。
![2-2-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-1_1%E6%9E%9A%E7%9B%AE.png)

- 以下の項目をそれぞれ選択・入力し、[関数の作成]をクリックします。
  - 一から作成
  - 関数名： 任意の名前（例：yamada_lambda_authentication）
  - ランタイム： `Python 3.7`
  - アクセス権限：[ ▼ 実行ロールの選択または作成]を開き、**「基本的なLambdaアクセス権限で新しいロールを作成」** を選択する
![2-2-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-1_2%E6%9E%9A%E7%9B%AE.png)
![2-2-1_3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-1_3%E6%9E%9A%E7%9B%AE.png)

「基本的なLambdaアクセス権限」を指定することで、Lambda実行時のログをCloudWatch Logsにアップロードするためのロールが自動的に付与されます。
次のステップで、Lambdaのソースコードから使用するAWSサービスに対する必要な権限をカスタムで追加します。


### 2-1-2. Lambdaに必要な権限を付与する

- 関数が作成された関数の画面に遷移します。
- 画面下部の実行ロール欄の「xxxxxxxxx-role-xxxxxxxxロールを表示」をクリックします。
- このLambdaに紐づいたロール詳細画面が開きます。
![2-2-2_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_1%E6%9E%9A%E7%9B%AE.png)
![2-2-2_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_2%E6%9E%9A%E7%9B%AE.png)
![2-2-2_3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_3%E6%9E%9A%E7%9B%AE.png)

- ロール詳細画面の「インラインポリシーの追加」をクリック
- Rekognitionのコレクションへのアクセスができるように、以下の権限をインラインポリシーとして追加し、任意の名前で登録しましょう

  - **Rekognitionのコレクションにアクセスする**

    - サービス： `Rekognition`
    - アクション：[読み込み] `SearchFacesByImage`
    - リソース：[指定]を選択し、collection欄の[ARNを指定]をクリックし、それぞれ登録します
      - Region： `ap-northeast-1`
      - Account： すべてにチェック
      - Collection Id：ステップ2-1-5で作成したコレクション名 (例： `yamada-authentication-collection`)


![2-2-2_5](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_0.png)
![2-2-2_6](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_%E7%A2%BA%E8%AA%8D.png)


### 2-1-3. Pythonの関数コードを作成する
    
Lambdaが実行するPythonコードを作成します。

- Lambdaの関数画面に戻ってください

- 「関数コード」欄のヘッダー部の右端に「ハンドラ」として `lambda_function.lambda_handler`がデフォルトで指定されています。
  これは、当Lambdaが呼び出された際に実行される関数が `lambda_function.py`の中の`lambda_handler`という関数だ、という意味です。

- サンプルプログラムは[こちら](https://github.com/IoTkyoto/iot-handson-rekognition/blob/master/step2/lambda_authentication.py)の `lambda_authentication.py`をご確認ください。

- サンプルプログラムの内容をコピーし、関数コード欄にペーストしてください

<!-- TODO: 行数確認 -->
- コードの14行目の以下の部分の「`{collection_id}`」を、ステップ1-6-1で作成したコレクション名（例：`yamada-authentication-collection`）に変更してください

```python:変更前
  # Rekognitionで作成したコレクション名を入れてください
  COLLECTION_ID = '{collection_id}'
```
```python:変更後
  # Rekognitionで作成したコレクション名を入れてください
  COLLECTION_ID = 'yamada-authentication-collection'
```

- 右上の「保存」をクリックしてください
![2-2-3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-3.png)

#### 作成プログラムの解説

- import一覧
    - 必要なライブラリをimportしてください

```python:lambda_function.py
  import json                       # JSONフォーマットのデータを扱うために利用します
  import boto3                      # AWSをPythonから操作するためのSDKのライブラリです
  from datetime import datetime     # この関数を動かした（＝顔の認証を行なった）時間をtimestampとして作成するのに利用します
  import botocore.exceptions  # boto3の実行時に発生する例外クラスです
  import base64 # base64フォーマットの画像データをRekognitionが認識できる形に変換するのに利用します
```

- API Gatewayに投げ込まれたデータは、 `lambda_handler`の引数となっている `event`の中に `body`として渡されます
	- `body`はJSON形式で渡されますので、Pythonで処理できる形にするために `json.loads`メソッドを利用しましょう
	- 今回、APIが呼ばれる際のパラメーターとして、以下のデータを受け取ることを想定して実装します
		- `image_base64str`：認証を行いたい顔画像ファイル(pngもしくはjpeg)をbase64でエンコードしたデータ(文字列型)
		- `threshold`：Rekognition実行時、コレクションに登録している顔との一致度合いがいくら以上の時に結果を返すか、という閾値(%)(数値型)。オプション項目なので、設定しない場合はRekognitionが持つデフォルト値の80%が自動的にセットされます

- base64のメソッド `b64decode`を使用し、base64でエンコードされたデータをバイナリデータに変換する
  - APIが受け取ったデータ `image_base64str`の形式のままでは、下で説明するRekognitionへのアクセスに利用できません
  - 画像データをbase64フォーマットに変換すると、ツールによってはHTMLに埋め込む際などに便利な"data URI scheme"に沿った形式で出力されます（例： `data:image/png;base64,{base64のデータ}`。こちらの記述はRekognitionに渡す必要がないので、カンマ部分より前に何かあれば取り出す処理を行います

```python:lambda_function.py
  # 画像データから不要な値を抜き出す(コンマがない場合は不要な値がないとし、全文字列を利用)
  image_base64str = image_base64str[image_base64str.find(',') + 1 :]
  return base64.b64decode(image_base64str)
```
- boto3 client `rekognition`のメソッド `search_faces_by_image`を使用する
	- 引数として、APIから受け取るデータの他に対象のコレクションIDの指定が必要です。
	- こちらのドキュメントを参考に、実装してください：
		- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.search_faces_by_image
	- `Image`パラメーター内の `'Bytes'`は、画像のバイナリデータを指定します
	- `MaxFaces`は、指定した画像から検出する顔の最大数を指定します
  - `FaceMatchThreshold`は、一致と判断する閾値(%)を指定します

```python:lambda_function.py
  # RekognitionのClientを生成
  REKOGNITION_CLIENT = boto3.client('rekognition')
  # 画像とマッチする人物を特定する
  search_result = REKOGNITION_CLIENT.search_faces_by_image(
      CollectionId=self.collection_id,
      Image={
            'Bytes': image_binary
      },
      MaxFaces=self.max_faces,
      FaceMatchThreshold=threshold
  )
```

- Lambdaの実行結果として返すレスポンスのボディとして、実際のデータを意味する `'payloads'`という辞書型のデータを作成しましょう
	- `'payloads'`の中に、`search_faces_by_image`の戻り値（辞書型）と `'timestamp'`属性を入れましょう
	- 下記の例のように `update`メソッドを利用すると、辞書型の中に辞書型のデータを入れることができます
		- `payloads.update(data)`（引数 `data`は `search_faces_by_image`の戻り値が格納されている変数）
	- `'timestamp'`の作成には、import一覧（例）にある標準モジュールの `datetime`が利用できます
	- `'timestamp'`の値のフォーマットは、可視化をする場合などに使いやすい`'YYYY-MM-DD hh:mm:ss'`が良いでしょう
	- レスポンスデータは `json.dumps`メソッドを利用してJSON形式にして返しましょう

```python:lambda_function.py
  # タイムスタンプ生成
  date_now = datetime.now()
  # 辞書型の変数定義
  payloads: dict = {}
  # タイムスタンプを設定
  payloads['timestamp'] = str(date_now.strftime('%Y-%m-%d %H:%M:%S'))
  # search_faces_by_imageの戻り値を設定
  payloads.update(search_result)
  # レスポンス用のBodyを生成
  body = json.dumps({'msg': msg, 'payloads': payloads})
```

- エラーハンドリングを実装する
try文を用いるなどして、Rekognitionへのアクセスの成否を反映したレスポンスを実装してみましょう。
なお、Lambda関数コード内で実装した `print()`メソッドによる出力は、CloudWatchのログで確認でき、通常はデバッグの用途で利用します。

### 2-1-4. Lambdaのテストを実行する

Lambdaの関数コードを保存したら、API Gatewayから渡されてくる想定のイベントデータを用意し、Lambdaに渡して、実際の動きをテストしてみましょう。

- 関数画面右上の[テスト]をクリックしてください。
![2-2-4_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-4_1.png)

- テストイベントの設定画面で以下の内容を入力して「作成」をクリックしてください。
  - 新しいテストイベントの作成：チェック
  - イベントテンプレート：Hello World（デフォルト）
  - イベント名：任意の名前（例：AuthTest）
  - テストデータ：以下のjsonファイルの内容。画像のデータや閾値を適宜変更してください。

- テストデータは[こちら](https://github.com/IoTkyoto/iot-handson-rekognition/blob/master/step2/lambda_authentication_event_example.json)の `lambda_authentication_event_example.json`をご確認ください。

- テストデータの内容をコピーし、テストイベントのコード欄に貼り付けてください

![2-2-4_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-4_2.png)

- 作成したら、[テスト]をクリックし、実行結果を確認しましょう。関数の実行結果は、中をスクロールして見ることが可能です
![2-2-4_3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-4_3.png)
![2-2-4_4](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-4_4.png)
![2-2-4_5](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-4_5.png)

- テストの結果として、「statusCode:200」と「ExternalImageId」として対象者のタグが返ってきていれば成功です。

## 2-2. API Gatewayを作成する

デバイス側から作成したLambdaを使用するために、API GatewayでREST APIを作成します。

### 2-2-1. APIを作成する

- AWSのコンソール画面で「API Gateway」を検索し、API Gatewayのコンソール画面を開きます。
- [+APIの作成]をクリックします。
![2-3-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-1_1%E6%9E%9A%E7%9B%AE.png)

- 以下の項目をそれぞれ入力し、[APIの作成]をクリックします。
    - プロトコルを選択する：`REST`
    - 新しいAPIの作成： **新しいAPI**
    - API名： 任意の名前（例：yamada-rekognition-api）
    - エンドポイントタイプ： **リージョン**
![2-3-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-1_2%E6%9E%9A%E7%9B%AE.png)

### 2-2-2. APIにリソースを追加する

作成直後のAPIには、具体的なアクセス先のリソースが存在していない状態です。
APIにリソースを追加し、ステップ2-2で作成したLambdaを呼び出すAPIリソースを作成します。

- 左メニューのAPI一覧で2-3-1で作成したAPIが選択されていることを確認する
- 「リソース」を選択する
- `/`が選択されている状態で「アクション」をクリックし「リソースの作成」を選択する
![2-3-2_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-2_1%E6%9E%9A%E7%9B%AE.png)

- 新しい子リソース画面で以下の内容を入力し「リソースの作成」をクリックする
  - プロキシリソースとして設定する：チェックなし
  - リソース名：search
  - リソースパス：search
  - API Gateway CORSを有効にする：チェック
![2-3-2_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-2_2%E6%9E%9A%E7%9B%AE_1_.png)

---

#### ＜リソースとは？＞

Amazon API Gatewayでは、API Gatewayリソースと呼ばれるプログラム可能なエンティティのコレクションとして REST API を構築できます。各 Resource エンティティは、Method リソースを 1 つ以上持つことができます。リクエストパラメーターと本文で表された Method は、クライアントが公開された Resource にアクセスするためのアプリケーションプログラミングインターフェイスを定義し、クライアントによって送信された受信リクエストを表します。
https://docs.aws.amazon.com/ja_jp/apigateway/latest/developerguide/how-to-create-api.html

#### ＜CORSとは？＞

Web APIは、元来パブリックに公開されず、リソースのオリジンが共有された一つのサービスの内部機能として利用されていました。そのことから、オリジンが異なるリソースからのアクセスを受けた際、デフォルトではアクセスを拒否してしまいます。CORSを設定することで、アクセス元のリソースを意識せずに利用することができるようになります。
https://docs.aws.amazon.com/ja_jp/apigateway/latest/developerguide/how-to-cors.html

---

### 2-2-3. APIにメソッドを追加する

APIにはHTTPメソッドが必要です。
ステップ2-2-3で作成したLambda実行コードに必要なデータをAPI経由で渡す必要があるため、レスポンスボディが使用できる`POST`にします。

- リソースで「`search`」が選択されている状態で「アクション」をクリックし「メソッドの作成」を選択する
![2-3-3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-3-1_.png)

- メソッド欄の「OPTIONS」の下にコンボボックスが表示されるため、「POST」を選択し☑️をクリックする

### 2-2-4. APIの統合先をセットする

APIメソッドを設定したら、バックエンドのエンドポイントに統合する必要があります。
バックエンドのエンドポイントは、統合エンドポイントとも呼ばれ、Lambda関数、HTTPウェブページ、または AWSのサービスアクションとして使用できます。
今回は、前ステップで作成したLambdaと統合しましょう。

- 「/search - POST - セットアップ」画面で以下の内容を入力し「保存」をクリックする
  - 統合タイプ：Lambda 関数  
  - Lambda プロキシ統合の使用：チェックを入れる
  - Lambda リージョン：`ap-northeast-1`
  - Lambda 関数：ステップ2-1-1で作成したLambda関数を入力（例：yamada_lambda_authentication）
  - デフォルトタイムアウトの使用：チェックを入れる
![2-3-4_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-4_1%E6%9E%9A%E7%9B%AE.png)

- [保存]をクリックすると、当該APIリソースが上で指定したLambda関数にアクセスするためのIAM権限を自動で作成するか確認されるため[OK]をクリックする
![2-3-4_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-4_2%E6%9E%9A%E7%9B%AE_1_.png)

#### ＜Lambdaプロキシ統合とは？＞

Amazon API Gateway Lambdaプロキシ統合は、単一のAPIメソッドのセットアップでAPIを構築するシンプル、強力、高速なメカニズムです。
Lambdaプロキシ統合は、クライアントが単一のLambda関数をバックエンドで呼び出すことを可能にします。
クライアントがAPIリクエストを送信すると、API Gatewayは、統合されたLambda関数にリクエストをそのまま渡します。
このリクエストデータには、リクエストヘッダー、クエリ文字列パラメータ、URLパス変数、ペイロード、および API設定データが含まれます。
バックエンドLambda関数では、受信リクエストデータを解析して、返すレスポンスを決定します。

詳細は[公式ドキュメント](https://docs.aws.amazon.com/ja_jp/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html)をご確認ください。

### 2-2-5. APIへのアクセスにAPIキーを必要とする設定にする

APIを公開すると、エンドポイントURLを知っている人は誰でもアクセス可能となります。
今回作成するAPIには、簡易な認証機能としてAPIキーによる認証を追加しましょう。

- 対象のメソッドを選択して「メソッドリクエスト」をクリックする
- メソッドリクエスト画面の設定欄の「APIキーの必要性」を `true`に変更する
![2-3-5](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-5.png)
*OPTIONSメソッドの「APIキーの必要性」は `true`にする必要はありません。*

#### ＜OPTIONSメソッドとは？＞
OPTIONSメソッドは、リソース作成時にCORSを有効にすることで自動的に作成されます。
このメソッドは、リソースに対するアクセスの際に、必ず最初に経由されます。
これにより、受け取ったリクエストのオリジンをOPTIONSのものと置き換えることで、オリジンの違いによるアクセス拒否を回避しています。

### 2-2-6. APIをデプロイする

作成したAPIは、デプロイすることで外部からアクセスすることが可能となります。
作成したAPIをデプロイしてみましょう。

- 対象APIのリソース「`/`」を選択した状態で、「アクション」をクリックし「APIのデプロイ」を選択する
![2-3-6_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-6_1%E6%9E%9A%E7%9B%AE.png)

- 「デプロイされるステージ」で `[新しいステージ]`を選択する
- 以下の項目を入力し「デプロイ」をクリックする
  - ステージ名：任意のステージ名（例：prod）
  - ステージの説明：任意
  - デプロイメントの説明：任意
![2-3-6_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-6_2%E6%9E%9A%E7%9B%AE.png)

- prodステージエディターが表示されればデプロイは完了
![2-3-6_4](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-7_8%E6%9E%9A%E7%9B%AE.png)

ステージは、APIを公開後も安定してAPIのエンドポイントを供給しながら開発を行う上で必須の機能です。

#### ＜API Gatewayのステージとは？＞

ステージは、デプロイに対して名前を付けたAPIのスナップショットとなります。
API Gatewayでは、ステージごとに別の設定やステージごとの変数を定義することが出来ます。
また、APIにアクセスするエンドポイントURLにはステージ名が含まれますので、例えば「v1.0」「v2.0」というステージを用意して
過去バージョンを保証したデプロイや、ステージを利用したカナリアリリースが可能となります。
詳細は[公式サイト](https://docs.aws.amazon.com/ja_jp/apigateway/latest/developerguide/set-up-stages.html)をご確認ください。

### 2-2-7. APIの使用量プランとAPIキーを作成する

APIキーに対して使用量プランを設定しましょう。
以下の説明を参考に紐付けるAPIキーでのアクセスの頻度を想定して、使用量を設定してください。

---

#### ＜使用量プランとは？＞
API Gatewayでは、使用量プランに紐付けたAPIキーの利用頻度を測定・制限することが可能です。
APIキーは使用できる回数分だけ「トークンバケット」に補給され、ここにある分だけがAPIへのアクセスに利用できます。
ページ内項目の「スロットリング」の「レート」は1秒ごとにトークンバケットに登録されるAPIキーを、「バースト」はバケットに入るトークンの最大数を表しています。
「クォータ」はある期間中にAPIキーが利用できる回数を示します。
この他にも様々な方法でAPIの利用を監視・制限できます。
詳細は[公式ドキュメント](https://docs.aws.amazon.com/ja_jp/apigateway/latest/developerguide/api-gateway-request-throttling.html)をご確認ください。

---

- 左のメニュー欄から「使用量プラン」を選択し「作成」をクリックする

- 使用量プランの作成画面で以下のように入力し「次へ」をクリックする
  - 名前：任意の名前（例：yamada-authentication-api-plan）
  - 説明：任意
  - スロットリングの有効化：チェックを入れる
    - レート：50
    - バースト：200
  - クォータを有効にする：チェックを入れる
    - クォータ：2000/ 月


- 関連付けられたAPIステージ画面で「APIのステージの追加」をクリックする
![2-3-7_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-7_1%E6%9E%9A%E7%9B%AE.png)

- APIの選択ボックスで作成したAPI（例：`yamada-rekognition-api`）を選択する
- ステージの選択ボックスで先ほどデプロイしたステージ（例：`prod`）を選択する
- 右端の☑️をクリックする
![2-3-7_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-7_2%E6%9E%9A%E7%9B%AE.png)

- 「次へ」をクリックする
![2-3-7_3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-7_3%E6%9E%9A%E7%9B%AE.png)


- 「APIキーを作成して使用量プランに追加」をクリックする
![2-3-7_4](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-7_4%E6%9E%9A%E7%9B%AE.png)

- APIキー画面で以下を入力し「保存」をクリックする
  - 名前：任意の名称（例：test-user）
  - APIキー：自動生成
  - 説明：任意
![2-3-7_5](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-7_5%E6%9E%9A%E7%9B%AE.png)

- 「完了」をクリックする
![2-3-7_6](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-7_6%E6%9E%9A%E7%9B%AE.png)

- これで、作成した使用量プランとデプロイしたAPIのステージ、そしてAPIキーが紐づきました。
  APIの使用量プランは、デプロイしたAPI Gatewayのステージと紐づきますので、ご注意ください。

### 2-2-8. cURLでAPIをテストする

cURLの `curl`コマンドを利用して、前のステップで作成したAPIにアクセスしてみましょう。

---

#### ＜cURLとは？＞

URLの書き方でファイルの送受信が行えるオープンソースのコマンドラインツールです。WebサイトやAPIサーバーのポート疎通確認によく利用され、HTTP/HTTPSの他にも様々なプロトコルに対応しています。コマンドラインで `curl`コマンドとして利用します。

---

今回、画像データが大きく、コマンドラインへの直接入力に向かないため、下記のshellファイルをコマンドラインから実行します。

- shellファイルは[こちら](https://github.com/IoTkyoto/iot-handson-rekognition/blob/master/step2/curl_test_authentication_format.sh)の `curl_test_authentication_format.sh`をご確認ください。

- 下記の解説に従い、shellファイルの中身を確認・編集してください。

#### curlコマンドの解説

**echoコマンドについて**

- 画像データが大きいため、`echo`コマンドを利用してAPIのリクエストボディに含めたいデータを出力します
- `echo`の引数である文字列内の`threshold`や `image_base64str`の値を書き換え、APIに投げ込むデータを適宜変更してください
- パイプ（ `|`）はデータの受け渡しを行います。今回の場合、 `echo`が出力したデータを次のコマンド、つまり `curl`に渡します

**curlコマンドについて**
- `-X`でHTTPメソッド `POST`を指定します
- 引数でAPIのURLを記述します。URLをダブルクォーテーションで囲み、 URL内の `{}`部分を下記を参考に変更してください
	- `{api_id}` → 下記の「APIのエンドポイントの確認方法」にあるAPIのエンドポイントのうち「.execute-api.api-northeast-1.~」の前の英数字部分
	- `{stage}` → ステップ2-2-6で作成したAPIをデプロイしたステージ名（例：prod）
	- `{resource}` → ステップ2-2-2で作成したAPIのリソース名（例：search）
- `-H`でヘッダーを表します
	- ステップ2-2-7で作成したAPIキーを、 `-H "X-Api-Key: {api_key}"`という形式で記述します。下記「APIキーの確認方法」に沿って確認してください

- `-d`でデータを表します。ここでは、パイプ経由で渡された値を表す `-@`を指定します

**APIのエンドポイントの確認方法**

AWSのコンソールで、ステップ2-2-6でデプロイしたAPIのステージを選択し、さらにリソースを選択すると、「URLの呼び出し」でAPIのリソースパスが表示されます。

![2-4-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-7_7%E6%9E%9A%E7%9B%AE.png)

**APIキーの確認方法**

AWSのコンソールで、ステップ2-2-7で作成したAPIキーを[表示]します。

![2-4-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-7_9%E6%9E%9A%E7%9B%AE.png)

- 変数の入力が終わったら、ファイルを保存し、実行します

- 現在コマンドラインがいるディレクトリを鑑みて、shellファイルが存在するディレクトリを正しく指定するようご注意ください。タブキーでの引数の自動補完を活用しましょう

```shell:実行コマンド例
sh curl_authentication_test_format.sh
```

- コマンドを実行すると、Lambda側で実装したレスポンスが返ってきます。

```shell:実行結果
sh curl_authentication_test_format.sh
{"msg": "[SUCCEEDED]Rekognition done", "payloads": {"timestamp": "2019-08-19 00:40:17", 
"SearchedFaceBoundingBox": {"Width": 0.24594193696975708, "Height": 0.45506250858306885, 
"Left": 0.21459317207336426, "Top": 0.1758822500705719}, "SearchedFaceConfidence": 99.99996185302734, 
"FaceMatches": [{"Similarity": 97.72643280029297, "Face": {"FaceId": "xxxxxx-xxxx-xxxx-xxxx-xxxxxx", 
"BoundingBox": {"Width": 0.40926501154899597, "Height": 0.44643399119377136, "Left": 0.2812440097332001, 
"Top": 0.12307199835777283}, "ImageId": "xxxxxxx-xxxx-xxxx-xxxx-xxxxxx", "ExternalImageId": "Taro_Yamada", 
"Confidence": 100.0}}], "FaceModelVersion": "4.0", "ResponseMetadata": {"RequestId": "xxxxx-xxxx-xxxx-xxxx-xxxxxx", 
"HTTPStatusCode": 200, "HTTPHeaders": {"content-type": "application/x-amz-json-1.1", "date": "Mon, 19 Aug 2019 00:40:16 GMT", 
"x-amzn-requestid": "xxxxxx-xxxx-xxxx-xxxx-xxxxxx", "content-length": "537", "connection": "keep-alive"}, 
"RetryAttempts": 0}}}
```

<!-- ここから要修正！スマホからAPIにアクセスする -->

## 2-3. デバイスからプログラムでWeb APIを利用する

### 2-3-1. 顔認証を行うWeb APIにアクセスするプログラムを作成する

最後に、ステップ0で作成したWebアプリケーションから、前のステップで作成したAPIのリソースにアクセスするVue.jsのプログラムを作成します。今回利用しているWebアプリケーションは、設定画面にユーザーが入力した値を元にAPIにアクセスするため、コード自体の修正は不要です。ここでは、コードを適宜引用しながら、APIにアクセスしている部分の解説のみを行います。

- Webアプリケーションのリポジトリを開き、以下のファイルを開いてください
  - `/handson_image_recognition_web/src/components/SearchFaces.vue`

#### 作成プログラムの解説

<!-- TODO: 全て行数確認 -->

##### `<template></template>`タグ内の要素について

- templateタグ内には、画面に表示する要素をHTMLで記述します
- コードの26行目のformタグ( `v-text-field`)内にある「`v-model="apiEndpoint"`」および27行目の「 `v-model="apiKey"`」の `v-model`は、このフォームに入力された値をそれぞれ " `apiEndpoint`(APIのエンドポイントの変数)" " `apiKey`(APIキーの変数)"プロパティとしてリアルタイムに反映・保持します
- コードの30行目のselectタグ( `v-select`)内でも、 `v-model`を利用し" `threshold`(閾値)"の値を保持します。選択可能な要素は、 `:items="[10,20,30,40,50,60,70,80,90,100]"`で指定しています
- コードの46行目のinputタグ( `v-file-input`)内にある「 `@change="onFileChange"`」は、ここに要素が入力されたことをトリガーに実行したい関数を表しています
- コードの82行目のbuttonタグ( `v-btn`)内にある「 `@click="execRecognition"`」は、ボタンクリック時に実行したい関数を表しています

##### `<script></script>`タグ内の要素について

- 必要なライブラリのimport定義をします

```javascript:SearchFaces.vue
  import axios from 'axios'; // APIエンドポイントにアクセスするのに利用します"
```

- APIへのアクセスに必要なパラメータを準備する
  - リクエストヘッダー情報

APIキーを、`'x-api-key': 'xxxxxxxxxxxxxxxxxxxxxxxx'`という形式で、ヘッダー情報に組み込みます。
また、やり取りするデータ形式を指定するため `'Content-type': 'application/json'`も入れましょう。
`this.apiKey`で、このコンポーネントが持つ`apiKey`プロパティの値を取得できます。ここでは、コードの27行目で画面から入力された値が最新値として代入されます。

```javascript:SearchFaces.vue
// コンポーネント内で利用する変数の初期値を設定する
data: () => ({
  // --他のデータ定義は省略--
  apiKey: '', 
}),

// ヘッダー情報を作成する
const config = {headers: {
  'Content-Type': 'application/json',
  'x-api-key': this.apiKey,
}};
```

  - リクエストボディ情報

ステップ2-1-3で作成したLambda関数コードが想定しているデータの値を用意します。
`base64data`には、 `createImage()`関数内の `FileReader`メソッドの実行結果として画像ファイルのbase64データ（data URI scheme形式）を利用します。
`threshold`では、`this.threshold`で、コードの30行目で画面で選択された値を最新値として利用します。

```javascript:SearchFaces.vue
// コンポーネント内で利用する変数の初期値を設定する
data: () => ({
  // --他のデータ定義は省略--
  base64data: '',
  // デフォルト値として初期値に80を設定
  threshold: 80,
}),

// リクエストボディ情報を作成する
const querydata = {
  'image_base64str': this.base64data,
  'threshold': this.threshold,
};

// 入力されたファイルをFileReaderでbase64(data URI scheme)にエンコードする
createImage(file) {
  const reader = new FileReader();
  
  reader.onload = e => {
    // ここにファイルの読み込み処理(readAsDataURL())実行後の処理を記述
    // 以下は画面表示のための要素に利用します
    this.uploadedImage = e.target.result;
    // 以下をAPIアクセスに利用します
    this.base64data = e.target.result;
  };
  // data URI scheme形式でファイルを読み込む
  reader.readAsDataURL(file);
},
```

- APIにアクセスする

最後に、`axios`を利用してリクエストを投げます。
`apiEndpoint`では、`this.apiEndpoint`で、コードの26行目で画面に入力された値を最新値として利用します。
リクエストボディのデータは `JSON.stringify()`メソッドでJSON形式に変換しましょう。

```javascript:SearchFaces.vue
// コンポーネント内で利用する変数の初期値を設定する
data: () => ({
  // --他のデータ定義は省略--
  info: '',
  apiEndpoint: '',
}),

axios
// APIエンドポイント、リクエストボディ、ヘッダーを引数にPOSTします
.post(this.apiEndpoint, JSON.stringify(querydata), config)
// APIアクセス成功時の処理です
.then(response => {
    // response.dataでレスポンスボディにアクセスします
    this.info = response.data;
    // ステップ2-1-3で作成した `payloads`内にあるRekognitionの結果データを取得します
    const faceMatches = this.info.payloads.FaceMatches;
    if (faceMatches.length == 0) {
      // 該当する人物がない場合に実行する処理を記述します
    } else {
      // 該当する人物がいた場合に実行する処理を記述します
    }
})
// エラーハンドリングを実装します
.catch(error => {
  // Lambdaからのエラーにはレスポンスデータがあるので、エラーメッセージを取得します
  if ('response' in error) {
    this.errorMessage = error.response.data.msg;
  } else {
    // API実行エラーやネットワークエラーの場合、errorにプロパティがありません
    this.errorMessage = error;
  }
});
```

- 実行結果を `console.log()`する
  プログラム実行結果をブラウザのデベロッパーツールのコンソールで確認できる様に`console.log()`メソッドで出力しましょう。デベロッパーツールは、Chromeの場合、「画面右上の設定ボタン > その他のツール > デベロッパーツール」で開くことができます。

<!-- ここから作業する -->

### 2-3-2. スマホ画面から顔認証を実行する

前のステップで作成したPythonファイルに引数を渡して実行します。
Pythonプログラム実行後の出力を確認します。
また、AWSのコンソールに移動し、CloudWatchでAPIへのアクセス履歴やLambdaのログを確認しましょう。

```python:実行結果
$ python3 execute_authentication_api.py image01_20190809094710.jpg yamada-target-images-bucket 80
{"msg": "[SUCCEEDED]Rekognition done", "payloads": {"timestamp": "2019-08-19 00:27:50", "SearchedFaceBoundingBox": 
{"Width": 0.24594193696975708, "Height": 0.45506250858306885, "Left": 0.21459317207336426, "Top": 0.1758822500705719}, 
"SearchedFaceConfidence": 99.99996185302734, "FaceMatches": [{"Similarity": 97.72643280029297, 
"Face": {"FaceId": "xxxxx-xxxx-xxxx-xxxx-xxxxxx", "BoundingBox": {"Width": 0.40926501154899597, 
"Height": 0.44643399119377136, "Left": 0.2812440097332001, "Top": 0.12307199835777283}, 
"ImageId": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxx", "ExternalImageId": "Taro_Yamada", "Confidence": 100.0}}], 
"FaceModelVersion": "4.0", "ResponseMetadata": {"RequestId": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxx", "HTTPStatusCode": 200, 
"HTTPHeaders": {"content-type": "application/x-amz-json-1.1", "date": "Mon, 19 Aug 2019 00:27:49 GMT", 
"x-amzn-requestid": "xxxxx-xxxx-xxxx-xxxx-xxxxxx", "content-length": "537", "connection": "keep-alive"}, 
"RetryAttempts": 0}}}
```
