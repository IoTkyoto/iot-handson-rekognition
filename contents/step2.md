# ステップ2. 顔認証のWeb APIを作成する（スマートフォンとAWSサービスを用いた画像認識サービスの構築する）

*当コンテンツは、エッジデバイスとしてスマートフォン、クラウドサービスとしてAWSを利用し、エッジデバイスとクラウド間とのデータ連携とAWSサービスを利用した画像認識を体験し、IoT/画像認識システムの基礎的な技術の習得を目指す方向けのハンズオン(体験学習)コンテンツ「[スマートフォンとAWSサービスを用いた画像認識サービスの構築する](https://qiita.com/kyoso_bizdev/private/e5c252f08de019ab8a1b)」の一部です。*

# ステップ2. 顔認証のWeb APIを作成する

![ステップ2アーキテクチャ図](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/architecture_step2.png)

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


## 2-1. 認識したい顔画像をアップロードするためのS3バケットを作成

この項目では、ステップ1-1と同様の手順で、画像認識の対象としてスマホからアップロードする画像の保存先となるバケットを作成していきます。
一点、前回との違いとして、S3バケット内のデータにライフサイクルを設定します。画像認識用にデバイスから送信された画像は長期間保存する必要はありませんので、オブジェクト作成から１日で削除されるように設定します。

### 2-1-1. AWSのコンソール画面で「S3」を検索・選択し[バケットを作成する]をクリックする

![1-1-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-1-1_1.png)

![1-1-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-1-1_2.png)

### 2-1-2. バケット名を入力し[次へ]をクリックする

- バケット名：任意の名称（例：yamada-rekognition-target-images）
- リージョン：アジアパシフィック（東京）
- 既存のバケットから設定をコピー：ブランク

![1-1-2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-1-2_1.png)

**【注意】 バケット名の一意性**

Amazon S3のバケット名はグローバルに一意であり、名前空間はすべてのAWSアカウントによって共有されています。
そのためバケット名は世界で一意のものを指定する必要があります。
重複するバケット名がすでに他の誰かに作成されている場合、その名前は利用できません。
S3バケットの命名のガイドラインについては[バケットの制約と制限](https://docs.aws.amazon.com/ja_jp/AmazonS3/latest/dev/BucketRestrictions.html)のサイトを参照してください。

**【注意】 リージョン指定**

リージョンが「アジアパシフィック(東京)」になっていることを確認してください。
今回はすべてのAWSサービスを東京リージョンで構築します。
リージョンが異なると、サービス間連携の遅延や他のAWSサービスと連携する上での困難等が生じることがございます。

### 2-1-3. 「オプションの設定」は何も設定せずに[次へ]をクリックする

今回はオプションの設定は使用しませんので、何もチェックをつけずに「次へ」をクリックしてください。

![1-1-3](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-1-3_1.png)

### 2-1-4. 「アクセス許可の設定」を確認し[次へ]をクリックする

アクセス許可の設定では、S3バケットに対してアクセスできる権限を指定します。
「**パブリックアクセスをすべてブロック**」にチェックが入っているかを確認してください。

**【注意】 S3バケットのパブリックアクセスについて**
「パブリックアクセスが有効」な状態のS3バケットは、世界中の人々に公開されている状態となります。
S3バケットのパブリックアクセスが原因となった顧客情報の漏洩などの事件も発生しておりますので、アクセス権限の設定はお気をつけください。
![1-1-４](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step1/1-1-3_2枚目_.png)


### 2-1-５. 確認画面に表示されている内容を確認し[バケットを作成]をクリックする

バケットの作成リージョンが「アジアパシフィック（東京）」になっていることや、パブリックアクセスをブロックするようになっていることを確かめてからバケットを作成します。

![1-1-５](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step1/1-1-4.png)


## 2-2. バケットのライフサイクルを設定

S3にはオブジェクト単位に設定可能なライフサイクル管理の機能があります。
これはオブジェクトがライフサイクルを通じてコスト効率の高い方法で保存されるように管理する仕組みです。
オブジェクト作成からの経過日数をトリガーとして、よりコスト効率の高いストレージクラスへの移行やオブジェクトの削除を行うことが出来ます。
詳細については公式ドキュメント「[オブジェクトのライフサイクル管理](https://docs.aws.amazon.com/ja_jp/AmazonS3/latest/dev/object-lifecycle-mgmt.html)」をご確認ください。



### 2-2-1. [管理]の[ライフサイクル]から[ライフサイクルルールの追加]をクリックする

- バケット検索に先ほど作成したバケットの名前の先頭数文字を入力し絞り込み、対象のバケット名をクリックする
- 「管理」タブをクリックし、「＋ライフサイクルルールの追加」をクリックする
![1-2-1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step1/1-2-1_.png)

### 2-2-2. ルール名を入力して[次へ]をクリックする

- ルール名：任意の名称（例：remove-in-a-day）
- フィルターを追加してプレフィックス/タグのみを対象にする：ブランク

![1-2-2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step1/1-2-2_.png)

### 2-2-3. 「移行」は今回は指定せず[次へ]をクリックする

「移行」設定をすると、オブジェクトが作成されてから指定した日数の経過をトリガーに、S3 GlacierサービスなどS3の別のストレージクラスにオブジェクトを移行することができるので、より無駄なコストを削減できます。

![1-2-3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step1/1-2-3.png)

---

#### ＜S3 Glacierとは？＞

Amazon S3 Glacierとは、データアーカイブ、および長期バックアップのためのセキュアで耐久性に優れた**超低コスト**のクラウドストレージサービスです。
通常のS3と比べると大幅にコストは低くなりますが、データ取り出しに非常に時間がかかります。

- データ取得の速度によって３つのデータ取得オプションを提供します。
    - 高速取得・・・１分〜５分
    - 標準取得・・・３時間〜５時間
    - バルク取得・・・５時間〜１２時間

より詳しく知りたい場合は[公式サイト](https://aws.amazon.com/jp/glacier/)をご確認ください。

---

### 2-2-4. 有効期限では「現行バージョン」「以前のバージョン」のいずれにもチェックを入れ、削除までの期間を設定する

![1-2-4](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step1/1-2-4.png)

### 2-2-5. 確認画面に表示されている内容で間違いがなければ[保存]をクリックする

![1-2-5](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step1/1-2-5.png)


## 2-3. Lambdaを作成

ここでは、スマホからアップロードする顔認証対象画像をステップ2-1で作成したS3バケットに保存した上で、この画像がステップ1で作成したRekognitionのコレクションに登録済みの人物とマッチするかどうか、マッチする場合は誰であるかリターン値として返すLambdaファンクションを作成します。

### 2-3-1. Lambda関数を作成する

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


### 2-3-2. Lambdaに必要な権限を付与する

- 関数が作成された関数の画面に遷移します。
- 画面下部の実行ロール欄の「xxxxxxxxx-role-xxxxxxxxロールを表示」をクリックします。
- このLambdaに紐づいたロール詳細画面が開きます。
![2-2-2_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_1%E6%9E%9A%E7%9B%AE.png)
![2-2-2_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_2%E6%9E%9A%E7%9B%AE.png)
![2-2-2_3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_3%E6%9E%9A%E7%9B%AE.png)

- ロール詳細画面の「インラインポリシーの追加」をクリック
- Rekognitionのコレクションへのアクセスや、顔認証のターゲットとなる画像のS3へのアップロードとアクセスができるように、以下の権限をインラインポリシーとして追加し、任意の名前で登録しましょう

  - **Rekognitionのコレクションにアクセスする**

    - サービス： `Rekognition`
    - アクション：[読み込み] `SearchFacesByImage`
    - リソース：[指定]を選択し、collection欄の[ARNを指定]をクリックし、それぞれ登録します
      - Region： `ap-northeast-1`
      - Account： すべてにチェック
      - Collection Id：ステップ2-1-5で作成したコレクション名 (例： `yamada-authentication-collection`)

  - **顔認証のターゲットとなる画像データをS3にアップロードする・S3に保存された画像データにアクセスする**

    - サービス： `S3`
    - アクション：[読み込み] `GetObject`・[書き込み] `PutObject`
    - リソース：[指定]を選択し、object欄の[ARNを指定]をクリック。ステップ1-1で作成したバケット名（例： `yamada-rekognition-target-images`）を入力し、Objectは[すべて]にチェック

  *「顔認証のターゲットとなる画像データをS3にアップロードする・S3に保存された画像データにアクセスする」には、ステップ2-1で作成したデバイスからアップロードした顔画像を保存するS3バケット名が必要です。
  ステップ1-1で作成した「コレクションに追加する顔の画像をアップロードするためのS3バケット」ではありませんので注意しましょう。*
![2-2-2_5](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_0.png)
![2-2-2_6](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_%E7%A2%BA%E8%AA%8D.png)


### 2-3-3. Pythonの関数コードを作成する

<!-- TODO: コード実装しながら修正する
    - （受け取ったデータのバリデーションチェック）
    - 引数の一つであるbase64データをデコード・S3バケットにPutObjectする
    - 上で保存したパスと・顔コレクション名（定数）、そして２つ目の引数である閾値データを使ってRekognitionを実行する
    - 認識結果をリターンする
- Lambdaのテストを行う
    - テスト用のJSONを作る：どれだけ一致度があれば返すか、の閾値設定
    - 画像データ（base64）→すごく大きくなるので、このテストに利用する.jsonファイルを作成する
- 顔認識用API（API Gateway）を作成する
- APIのテストを行う
- スマホから実行する
    - 入力項目
        - 画像データをアップロードする
        - 自分が作成したAPIのエンドポイント（部分的）
        - どれだけ一致度があれば返すか、の閾値設定
    - （確認）入力不要項目
        - 顔コレクションの名前はLambdaに定数としてハードコーディングする
    - 顔認識対象バケットの名前もLambdaに定数としてハードコーディングする -->
    
Lambdaが実行するPythonコードを作成します。

- Lambdaの関数画面に戻ってください

- 「関数コード」欄のヘッダー部の右端に「ハンドラ」として `lambda_function.lambda_handler`がデフォルトで指定されています。
  これは、当Lambdaが呼び出された際に実行される関数が `lambda_function.py`の中の`lambda_handler`という関数だ、という意味です。

- サンプルプログラムは[こちら](https://github.com/IoTkyoto/iot-handson-zybo-and-aws/blob/master/step2/lambda_authentication.py)の `lambda_authentication.py`をご確認ください。

- サンプルプログラムの内容をコピーし、関数コード欄にペーストしてください

- コードの13行目の以下の部分の「`{collection_id}`」をステップ1-6-1で作成したコレクション名（例：`yamada-authentication-collection`）に変更してください

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
  from botocore.exceptions import ClientError  # boto3の実行時に発生する例外クラスです
```

- API Gatewayに投げ込まれたデータは、 `lambda_handler`の引数となっている `event`の中に `body`として渡されます
	- `body`はJSON形式で渡されますので、Pythonで処理できる形にするために `json.loads`メソッドを利用しましょう
	- 今回、APIが呼ばれる際のパラメーターとして、以下のデータを受け取ることを想定して実装します
		- `bucket_name`：認証を行いたい顔画像を保存しているS3バケット名
		- `file_name`：上で指定したS3バケットに保存されている、認証を行いたい顔画像ファイル名
		- `threshold`：Rekognition実行時、コレクションに登録している顔との一致度合いがいくら以上の時に結果を返すか、という閾値(%)

- boto3 client `rekognition`のメソッド `search_faces_by_image`を使用する
	- 引数として、APIから受け取るデータの他に対象のコレクションIDの指定が必要です。
	- こちらのドキュメントを参考に、実装してください：
		- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.search_faces_by_image
	- `Image`パラメーター内の `'Bytes'`は、今回S3バケット内の画像を指定しているので、必要ありません
    <!-- 今回のRekognitionへのアクセス方法では、直接イメージのバイトデータを投げることも可能ですが、 ...-->
	- `'S3Object'`項目内の `'Version'` は、S3バケットのバージョンを意味します。今回は必要ありません
	- `MaxFaces`は、指定した画像から検出する顔の最大数を指定します
  - `FaceMatchThreshold`は、一致と判断する閾値(%)を指定します

```python:lambda_function.py
  # RekognitionのClientを生成
  REKOGNITION_CLIENT = boto3.client('rekognition')
  # 画像とマッチする人物を特定する
  search_result = REKOGNITION_CLIENT.search_faces_by_image(
      CollectionId=self.collection_id,
      Image={
            'S3Object': {
              'Bucket': s3_bucket,
              'Name': s3_obj
            }
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
	- `'timestamp'`の値のフォーマットは、後の可視化ステップに対応するために、`'YYYY-MM-DD hh:mm:ss'`となるようにしてください
	- レスポンスデータは `json.dumps`メソッドを利用してJSON形式にして返しましょう

```python:lambda_function.py
  # タイムスタンプ生成
  date_now = datetime.now()
  # dictionary型の変数定義
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

### 2-3-4. Lambdaのテストを実行する

Lambdaの関数コードを保存したら、API Gatewayから渡されてくる想定のイベントデータを用意し、Lambdaに渡して、実際の動きをテストしてみましょう。

- 関数画面右上の[テスト]をクリックしてください。
![2-2-4_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-4_1.png)

- テストイベントの設定画面で以下の内容を入力して「作成」をクリックしてください。
  - 新しいテストイベントの作成：チェック
  - イベントテンプレート：Hello World（デフォルト）
  - イベント名：任意の名前（例：AuthTest）
  - テストデータ：以下のテストデータ。実際に存在するバケット名やファイル名に置き換えてください。

```json:テストイベント用JSONデータ
  {
    "body": {
      "file_name": "image01_20190808181200.jpg",
      "bucket_name": "yamada-target-images-bucket",
      "threshold": 60,
      "image": ,
    }
  }
```

![2-2-4_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-4_2.png)

- 作成したら、[テスト]をクリックし、実行結果を確認しましょう。関数の実行結果は、中をスクロールして見ることが可能です。
![2-2-4_3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-4_3.png)
![2-2-4_4](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-4_4.png)
![2-2-4_5](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-4_5.png)

- テストの結果として、「statusCode:200」と「ExternalImageId」として対象者のタグが返ってきていれば成功です。

## 2-3. API Gatewayを作成する

デバイス側から作成したLambdaを使用するために、API GatewayでREST APIを作成します。

### 2-3-1. APIを作成する

- AWSのコンソール画面で「API Gateway」を検索し、API Gatewayのコンソール画面を開きます。
- [+APIの作成]をクリックします。
![2-3-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-1_1%E6%9E%9A%E7%9B%AE.png)

- 以下の項目をそれぞれ入力し、[APIの作成]をクリックします。
    - プロトコルを選択する：`REST`
    - 新しいAPIの作成： **新しいAPI**
    - API名： 任意の名前（例：yamada-rekognition-api）
    - エンドポイントタイプ： **リージョン**
![2-3-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-1_2%E6%9E%9A%E7%9B%AE.png)

### 2-3-2. APIにリソースを追加する

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

### 2-3-3. APIにメソッドを追加する

APIにはHTTPメソッドが必要です。
ステップ2-2-3で作成したLambda実行コードに必要なデータをAPI経由で渡す必要があるため、レスポンスボディが使用できる`POST`にします。

- リソースで「`search`」が選択されている状態で「アクション」をクリックし「メソッドの作成」を選択する
![2-3-3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-3-1_.png)

- メソッド欄の「OPTIONS」の下にコンボボックスが表示されるため、「POST」を選択し☑️をクリックする

### 2-3-4. APIの統合先をセットする

APIメソッドを設定したら、バックエンドのエンドポイントに統合する必要があります。
バックエンドのエンドポイントは、統合エンドポイントとも呼ばれ、Lambda関数、HTTPウェブページ、または AWSのサービスアクションとして使用できます。
今回は、前ステップで作成したLambdaと統合しましょう。

- 「/search - POST - セットアップ」画面で以下の内容を入力し「保存」をクリックする
  - 統合タイプ：Lambda 関数  
  - Lambda プロキシ統合の使用：チェックを入れる
  - Lambda リージョン：`ap-northeast-1`
  - Lambda 関数：ステップ2-2-1で作成したLambda関数を入力（例：yamada_lambda_authentication）
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

### 2-3-5. APIへのアクセスにAPIキーを必要とする設定にする

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

### 2-3-6. APIをデプロイする

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

### 2-3-7. APIの使用量プランとAPIキーを作成する

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

### 2-3-8. cURLでAPIをテストする

cURLの `curl`コマンドを利用して、前のステップで作成したAPIにアクセスしてみましょう。

---

#### ＜cURLとは？＞

URLの書き方でファイルの送受信が行えるオープンソースのコマンドラインツールです。WebサイトやAPIサーバーのポート疎通確認によく利用され、HTTP/HTTPSの他にも様々なプロトコルに対応しています。コマンドラインで `curl`コマンドとして利用します。

---

デバイスのコマンドラインに下記の例の通りコマンドを入力してください。

```shell:実行コマンド例
curl -X POST "https://{api_id}.execute-api.ap-northeast-1.amazonaws.com/{stage}/{resource}" \
-H "X-Api-Key: {api_key}" -H "Content-Type: application/json" \
-d "{\"file_name\":\"image01_20190808181200.jpg\",\"bucket_name\":\"yamada-target-images-bucket\",\"threshold\":60}"
```

#### curlコマンドの解説

- `-X`でHTTPメソッド `POST`を指定します
- 引数でAPIのURLを記述します。URLをダブルクォーテーションで囲み、 URL内の `{}`部分を下記を参考に変更してください
	- `{api_id}` → 下記の「APIのエンドポイントの確認方法」にあるAPIのエンドポイントのうち「.execute-api.api-northeast-1.~」の前の英数字部分
	- `{stage}` → 2-3-6で作成したAPIをデプロイしたステージ名（例：prod）
	- `{resource}` → 2-3-2で作成したAPIのリソース名（例：search）
- `-H`でヘッダーを表します。記述するヘッダーは下記の2つです
	- ステップ2-3-7で作成したAPIキーを、 `-H "X-Api-Key: {api_key}"`という形式で記述します。下記「APIキーの確認方法」に沿って確認してください
	- やり取りするデータ形式を指定するため `-H "Content-Type: application/json"`と記述します

- `-d`でデータを表します。2-2-4でLambdaのテストを行った時のデータを参考に、実際に存在するバケット名やファイル名に置き換えてください

**APIのエンドポイントの確認方法**

AWSのコンソールで、ステップ2-3-6でデプロイしたAPIのステージを選択し、さらにリソースを選択すると、「URLの呼び出し」でAPIのリソースパスが表示されます。

![2-4-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-7_7%E6%9E%9A%E7%9B%AE.png)

**APIキーの確認方法**

AWSのコンソールで、ステップ2-3-7で作成したAPIキーを[表示]します。

![2-4-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-3-7_9%E6%9E%9A%E7%9B%AE.png)

- コマンドを実行すると、Lambda側で実装したレスポンスが返ってきます。

```shell:実行結果
curl -X POST "https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prod/search" \
-H "X-Api-Key: xxxxxxxxxxxxxxxx" -H "Content-Type: application/json"　\
-d "{\"file_name\":\"image01_20190808181200.jpg\",\"bucket_name\":\"yamada-target-images-bucket\",\"threshold\":60}"
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

## 2-4. デバイスからプログラムでWeb APIを利用する

### 2-4-1. 顔認証を行うWeb APIにアクセスするプログラムを作成する

最後に、前のステップで作成したAPIのリソースに対して、POSTメソッドでアクセスするPythonプログラムを作成します。

Pythonプログラムの書き方は、ステップ1-4-2を参考にしてください。

今回は、コマンド引数として

- 第1引数：pythonファイル（例: `execute_authentication_api.py`）
- 第2引数：ステップ1-1で作成したS3にアップロードした画像ファイル名（例: `image01_20190809094710.jpg`）
- 第3引数：ステップ1-1で作成したS3のバケット名（例: `yamada-target-images-bucket`）
- 第4引数：Rekognition実行時、コレクションに登録している顔との一致度合いがいくら以上の時に結果を返すか、という閾値（%）

を指定することで動作するプログラムを作成します。

```shell:実行コマンド例
$ python3 execute_authentication_api.py image01_20190809094710.jpg yamada-target-images-bucket 80
```

- サンプルプログラムは[こちら](https://github.com/IoTkyoto/iot-handson-zybo-and-aws/blob/master/step2/execute_authentication_api.py)の `execute_authentication_api.py`をご参考ください。

- サンプルプログラムの内容をコピーし、関数コード欄にペーストし、コード内の以下の部分を変更してください
    - 18行目「`API_KEY =  'xxxxxxxxxxxxxxxxxxx'`」 → 2-3-8「APIキーの確認方法」を参照
    - 20行目「`STAGE = 'xxxxxx'`」 → 2-3-6で作成したAPIをデプロイしたステージ名（例：prod）
    - 22行目「`API_ID = 'xxxxxx'`」 → 2-3-8「APIのエンドポイントの確認方法で確認したエンドポイントのうち「`.execute-api.api-northeast-1.~`」の前の英数字部分
    - 24行目「`RESOURCE = 'xxxxxx'`」 → 2-3-2で作成したAPIのリソース名（例：search）

```python:変更例
# APIキーの指定
API_KEY =  'ABCDEFGHIJK12345'
# APIのステージ
STAGE = 'prod'
# APIのID
API_ID = 'abcde123'
# APIのリソースパス
RESOURCE = 'search'
BASE_URL = 'https://{api_id}.execute-api.ap-northeast-1.amazonaws.com/{stage}/{resource}'
```

#### 作成プログラムの解説

- import一覧（例）

```
import sys               # pythonコマンド実行時に指定された引数を取得するのに利用します
import json              # JSONフォーマットのデータを扱うために利用します
import urllib.request    # RestAPIへのアクセスを行える簡易なライブラリです
```

- `urllib.request`モジュールを利用してRestAPIにアクセスする
	- 追加のモジュールのインストールが不要なPythonの標準ライブラリです。こちらのドキュメントを参考に実装してください：
	- https://docs.python.org/ja/3/library/urllib.request.html
	- より具体的な書き方については、上述の実際のプログラム例（ `execute_authentication_api.py`）をご参考ください。

- リクエストヘッダー情報
APIキーを、`'x-api-key': 'xxxxxxxxxxxxxxxxxxxxxxxx'`という形式で、ヘッダー情報に組み込みます。
また、やり取りするデータ形式を指定するため `'Content-type': 'application/json'`も入れましょう。

- リクエストボディ情報
ステップ2-2-3.で作成したLambda関数コードが想定しているデータの値を用意します。
Pythonプログラムの第2引数を `file_name`の、第3引数を `bucket_name`の、そして第4引数を `threshold`のデータ値としそれぞれセットします。
最後に、リクエストボディのデータを `json.dumps`メソッドでJSON形式に変換しましょう。

- 実行結果を `print()`する
	プログラム実行結果をコマンドラインで確認できるように、 `print()`メソッドで出力しましょう。
	try文を用いるなどして、成否それぞれの場合の出力を実装してみましょう。

### 2-4-3. Pythonプログラムを実行する

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

### 2-4-4. ステップ1で作成したプログラムからcallさせる
単体で実行に成功したあとは、`1-6. ステップ2, ステップ3で実装するプログラムをcallするコードを追記する`でコメントアウトして追記した部分のコメントアウトを外し、ステップ1で実装したコードを実行してください。
これにより、デバイスから画像を投稿→顔認証の流れを検証することができます。

```python:upload_target_image.pyの26行目と90行目のコメントを解除
# ステップ2で構築するプログラムのパス
EXECUTE_AUTHENTICATION_PATH = '../step2/execute_authentication_api.py'

・・・（中略）・・・

# ステップ2で構築するプログラムをcallする
subprocess.call(["python3", EXECUTE_AUTHENTICATION_PATH, relation_s3.filename, args[2], '60'])
```

```shell:画像アップロードから画像認証まで続けて実施
$ python3 upload_target_image.py picture/image01.jpg yamada-target-images-bucket
[succeeded!] upload file name: image01_20190819094015.jpg
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
