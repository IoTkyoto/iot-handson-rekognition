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

- 顔認証用のWebAPIを作成し、デバイスからWebAPIを利用する
 - APIのリクエスト・レスポンスを取り扱う
 - WebAPIの認証はAPIキーを使う
- 顔認識用のコレクションを作成し、対象者が画像に写っているかどうかの画像認識を行う

<!-- 
- （確認）新アーキテクチャでは、ステップ１において以下のことを行う
    - 顔認識用のS3バケットを作成する
    - 上記バケットを利用し、顔コレクションを作成する
    - 顔認識用のバケットにアクセスし、顔コレクションを作成するIAMユーザークレデンシャルを発行しPCに持たせる
    - 顔認識の対象となる顔画像の置き場となるバケットは作成しない→ステップ２で作成する
    - 顔認識対象バケットに画像をアップロードしない→ステップ２でカバーする

- 以上を踏まえ、ステップ２で書く必要のある内容を整理
    - 顔認識対象バケットを作成する
        - オプションで画像のライフサイクルを設定する
    - 顔認識対象バケットにPutObject・ステップ1で作成した顔コレクションにアクセスできるIAMロールを作成する
        - つまづきポイント：権限がちゃんと選べているか
    - 顔認識用ロジック（Lambda）を作成する
        - （受け取ったデータのバリデーションチェック）
        - 引数の一つであるbase64データをデコード・S3バケットにPutObjectする
        - 上で保存したパスと・定数である顔コレクション、そしてもう一つの引数である閾値データを使ってRekognitionを実行する
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
            - 顔認識対象バケットの名前もLambdaに定数としてハードコーディングする
-->

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

## 2-1. Rekognitionのコレクションを作成する

顔認識を行うために、参照元となるRekognitionのコレクションを作成しましょう。

まずは、コレクションに登録するための画像を格納するS3バケットを作成します。
そして、作成したバケットに画像をアップロードした後、その画像を指定してコレクションに顔の登録を行います。

### 2-1-1. コレクション作成に利用するS3バケットを作成する

コレクションに顔を登録するためには、登録したい顔の画像をS3バケットにアップロードする必要があります。

- ステップ1-1を参考に、バケットを作成してください。
  - バケット名：任意の名称（例：yamada-rekognition-collection-source）
  - リージョン：アジアパシフィック（東京）
  - 既存のバケットから設定をコピー：ブランク
  - オプションの設定：すべて設定なし
  - アクセス許可の設定：パブリックアクセスをすべてブロックにチェック

*コレクションは登録に利用した画像データ自体を保持しません。
コレクションに登録した画像を後から確認出来るように、ライフサイクルの設定は行いません。*

### 2-1-2. S3バケットに画像をアップロードする

作成したバケットに、コレクションに登録したい顔画像をアップロードします。

- アップロードの作業に移る前に、下記注意事項をご確認ください。
  - **Rekognitionで利用できる画像の制限**
  Rekognitionに利用できる画像には制限がありますので、画像をアップロードする前にご確認ください。
  https://docs.aws.amazon.com/ja_jp/rekognition/latest/dg/limits.html
  - **画像に写っている顔の数**
  後述のRekognitionのコレクションへの顔の登録の性質から、画像に写っている顔は、登録したい人一人分の顔が写ったものを利用ください。

- 以下の手順で対象画像をアップロードしましょう
  - AWSのS3コンソールを開く
  - ステップ2-1-1で作成したバケットを開き「アップロード」をクリック
  - アップロード画面に顔認識のベースとなる画像をドロップ
  - オプションは何も指定せずに「アップロード」をクリック
  - アップロードに成功した場合、画像ファイルがバケット内にリストで表示される

### 2-1-3. Rekognitionのコレクションの作成とコレクションへの顔の追加ができる権限を作成する

現時点(2019/8/1時点)では、AWSのコンソール画面からRekognitionのコレクションは作成できません。
そのため、ローカルPCからAWS CLIを使用してRekognitionのコレクションを作成する必要がございます。
*※ローカルPCのAWS CLIにAdmin権限を付与済みであれば、当対応は不要です。*

ローカルPCのAWS CLIでRekognitionの操作を行うために必要なIAMの権限を作成します。
ステップ1-3.を参考に、IAMユーザーを作成し、アクセスキーをダウンロードしてください。

ポリシーの作成で必要な権限は以下の通りです。

- **ステップ2-1-1で作成したS3バケットにアクセスし、その中のオブジェクトをGetする** 

	- サービス： `S3`
	- アクション：[読み込み]の `GetObject`
	- リソース：[指定]を選択し、object欄の[ARNを追加]をクリック。ステップ2-1-1で作成したバケット名  
	　　　　　　（例： `yamada-rekognition-collection-source`）を入力し、Objectは[すべて]にチェック

- **Rekognitionでコレクションを扱う**

	- サービス： `Rekognition`
	- アクション：
		- [読み込み] `ListCollections`、 `ListFaces`、 `SearchFacesByImage
`
		- [書き込み] `CreateCollection`、 `IndexFaces`、 `DeleteCollection`、 `DeleteFaces`
	- リソース：すべてのリソース

※ 「Rekognitionでコレクションを扱う」権限では、コレクションの作成と顔の登録の他に、コレクションや登録した顔を確認・利用したり、ハンズオン後に削除するために必要な権限も付与しています。

#### 複数サービスを対象とするポリシーを作成する方法
ビジュアルエディタのポリシー作成画面にて、右下の[さらにアクセス許可を追加]をクリックすることで、一度に複数のサービスを対象とするポリシーを登録することができます。

### 2-1-4. クレデンシャル情報をAWS CLIに登録する

作成したクレデンシャル情報を、ローカルPCのAWS CLIに登録します。
登録の方法は、1-4-1を参考にしてください。

### 2-1-5. コレクションを作成する

まずは、認証の対象となる顔データの登録先となるコレクションを作成します。
コレクションには、 `--collection-id`パラメーターで名前をつける必要があります。
使用目的が分かるようなコレクション名をつけましょう。
（例：yamada-authentication-collection）

- 以下のコマンドを実行しコレクションを作成してください
  コマンドの詳細は、公式ドキュメント「[コレクションの作成](https://docs.aws.amazon.com/ja_jp/rekognition/latest/dg/create-collection-procedure.html)」をご確認ください。

```shell:実行コマンド例
# collection-id の引数は任意のコレクション名にしてください
$ aws rekognition create-collection --collection-id "yamada-authentication-collection"
```

- 出力結果から、コレクションが作成できたかどうかが確認できます

```shell:実行結果
$ aws rekognition create-collection --collection-id "yamada-authentication-collection"
{
    "StatusCode": 200,
    "CollectionArn": "aws:rekognition:ap-northeast-1:XXXXXXXXXXXX:collection/yamada-authentication-collection",
    "FaceModelVersion": "4.0"
}
```

- `list-collections`コマンドを実行することで、対象のAWSアカウントで管理されているコレクションの一覧を確認することができます

```shell:実行コマンド
$ aws rekognition list-collections
{
    "CollectionIds": [
        "authentication-collection",
        "collection-handson",
        "yamada-authentication-collection"
    ],
    "FaceModelVersions": [
        "4.0",
        "4.0",
        "4.0"
    ]
}
```

### 2-1-6. コレクションに顔を登録する

前のステップで作成したコレクションに対して、以下のコマンドで対象の顔画像を登録します。

```shell:実行コマンド例
$ aws rekognition index-faces \
      --image '{"S3Object":{"Bucket":"yamada-rekognition-collection-source","Name":"Taro_Yamada.jpg"}}' \
      --collection-id "yamada-authentication-collection" \
      --max-faces 1 \
      --quality-filter "AUTO" \
      --detection-attributes "ALL" \
      --external-image-id "Taro_Yamada" 
```

- **パラメーターの説明**
  コマンドの詳細は、[こちら](https://docs.aws.amazon.com/ja_jp/rekognition/latest/dg/add-faces-to-collection-procedure.html)の公式ドキュメントをご参考ください。

  - `--image`
      - パラメーター内の `"Bucket"`属性の値には、ステップ2-1-1で作成したバケット名、 
      - `"Name"`属性の値には、ステップ2-1-2でアップロードした画像ファイル名を、それぞれ入力します

  - `--collection-id`
      - 前のステップで作成したコレクション名を入力します

  - `--max-faces 1`
      - これは、登録に利用した画像に複数人写っていた場合、「顔である」確率が最も高いものから最大何人分の顔を一度に登録するかを指定しています。
      - Rekognitionのコレクションへの顔の登録では、画像に写っている顔を最大100人まで一度に登録できますが、その際につけられるタグは1つだけです。
      - 今回は、顔とタグを一対一で対応させたいので、 `max-faces`を `1`にしてください。。

  - `--external-image-id`
      - オプション指定例: `external-image-id "Taro_Yamada"`
      - これは、登録に利用した画像データに対して、タグ付けを行う機能です。
      - 上記の `--max-faces`を `1`と指定し、画像に写っている人物名を `external-image-id`で設定することで、コレクションを利用した顔認証の際に、判定結果の人物名を取得することが可能となります。


- コレクションに顔の登録が成功した場合は、対象の顔の特徴情報のJSONが表示されます

```shell:登録成功時
{
    "FaceRecords": [
        {
            "Face": {
                "FaceId": "XXXXX-XXXX-XXXX-XXXX-XXXXXXX",
                "BoundingBox": {
                    "Width": 0.40926530957221985,
                    "Height": 0.446433961391449,
                    "Left": 0.2812435030937195,
                    "Top": 0.12307235598564148
                },
                "ImageId": "XXXXX-XXXX-XXXX-XXXX-XXXXXXX",
                "ExternalImageId": "Taro_Yamada",
                "Confidence": 100.0
            },
          ・・・
```

- `list-faces` コマンドを実行することで、対象のコレクションに含まれる顔の一覧を確認することができます
  実行時には対象のコレクションIDを指定する必要があります

```shell:実行コマンド
$aws rekognition list-faces --collection-id yamada-authentication-collection
{
    "Faces": [
        {
            "FaceId": "XXXXX-XXXX-XXXX-XXXX-XXXXXXX",
            "BoundingBox": {
                "Width": 0.40926501154899597,
                "Height": 0.44643399119377136,
                "Left": 0.2812440097332001,
                "Top": 0.12307199835777283
            },
            "ImageId": "XXXXX-XXXX-XXXX-XXXX-XXXXXXX",
            "ExternalImageId": "Taro_Yamada",
            "Confidence": 100.0
        }
    ],
    "FaceModelVersion": "4.0"
}
```

### 2-1-7. コレクションをテストする

ステップ2-1-2で作成したバケットとアップロードした画像を利用して、コレクションに登録した顔とマッチするかテストします。コレクションに登録した顔のデータと、そのデータの元となる画像を比較するため、マッチ率は100%に限りなく近い数値となります。

- 以下のコマンドを実行し、指定した画像の中にコレクション内の顔と一致する顔があるか確認します

```shell:実行コマンド例
$ aws rekognition search-faces-by-image \
--image '{"S3Object":{"Bucket":"yamada-rekognition-collection-source","Name":"Taro_Yamada.jpg"}}' \
--collection-id "yamada-authentication-collection"
```

- **パラメーターの説明**
  コマンドの詳細は、[こちら](https://docs.aws.amazon.com/ja_jp/rekognition/latest/dg/search-face-with-image-procedure.html)の公式ドキュメントをご参考ください。

  - `--image`
      - パラメーター内の `"Bucket"`属性の値には、ステップ2-1-1で作成したバケット名、 
      - `"Name"`属性の値には、ステップ2-1-2でアップロードした画像ファイル名を、それぞれ入力します

  - `--collection-id`
      - 前のステップで作成したコレクション名を入力します
 
- 出力結果から、指定したS3バケット内の画像の中に顔があるかどうか、顔がコレクション内の顔とどの程度マッチするかがわかります
    -  `FaceMatches`内の要素のうち `Similarity`が、マッチ度を表し、
    -  マッチした顔は `Face`内の `ExternalImageId`で確認できます

```shell:実行結果
$ aws rekognition search-faces-by-image --image '{"S3Object":{"Bucket":"yamada-rekognition-collection-source","Name":"Taro_Yamada.jpg"}}' --collection-id yamada-authentication-collection

{
    "SearchedFaceBoundingBox": {
        "Width": 0.40926530957221985,
        "Height": 0.446433961391449,
        "Left": 0.2812435030937195,
        "Top": 0.12307235598564148
    },
    "SearchedFaceConfidence": 100.0,
    "FaceMatches": [
        {
            "Similarity": 99.99918365478516,
            "Face": {
                "FaceId": "XXXXX-XXXX-XXXX-XXXX-XXXXXXX"",
                "BoundingBox": {
                    "Width": 0.40926501154899597,
                    "Height": 0.44643399119377136,
                    "Left": 0.2812440097332001,
                    "Top": 0.12307199835777283
                },
                "ImageId": "XXXXX-XXXX-XXXX-XXXX-XXXXXXX",
                "ExternalImageId": "Taro_Yamada",
                "Confidence": 100.0
            }
        }
    ],
    "FaceModelVersion": "4.0"
}
```

## 2-2. Lambdaを作成する

ステップ2-1で作成したRekognitionのコレクションにアクセスし、指定したS3バケット内の画像がコレクションに登録済みの人物とマッチするかどうか、マッチする場合は誰であるかリターン値として返すLambdaファンクションを作成します。

### 2-2-1. Lambda関数を作成する

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


### 2-2-2. Lambdaに必要な権限を付与する

- 関数が作成された関数の画面に遷移します。
- 画面下部の実行ロール欄の「xxxxxxxxx-role-xxxxxxxxロールを表示」をクリックします。
- このLambdaに紐づいたロール詳細画面が開きます。
![2-2-2_1](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_1%E6%9E%9A%E7%9B%AE.png)
![2-2-2_2](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_2%E6%9E%9A%E7%9B%AE.png)
![2-2-2_3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_3%E6%9E%9A%E7%9B%AE.png)

- ロール詳細画面の「インラインポリシーの追加」をクリック
- Rekognitionのコレクションへのアクセスや、顔認証のターゲットとなる画像にアクセスできるように、以下の権限をインラインポリシーとして追加し、任意の名前で登録しましょう
  - **Rekognitionのコレクションにアクセスする**

    - サービス： `Rekognition`
    - アクション：[読み込み] `SearchFacesByImage`
    - リソース：[指定]を選択し、collection欄の[ARNを指定]をクリックし、それぞれ登録します
      - Region： `ap-northeast-1`
      - Account： すべてにチェック
      - Collection Id：ステップ2-1-5で作成したコレクション名 (例： `yamada-authentication-collection`)

  - **顔認証のターゲットなる画像データにアクセスする**

    - サービス： `S3`
    - アクション：[読み込み] `GetObject`
    - リソース：[指定]を選択し、object欄の[ARNを指定]をクリック。ステップ1-1で作成したバケット名（例： `yamada-target-images-bucket`）を入力し、Objectは[すべて]にチェック

  *「顔認証のターゲットとなる画像データにアクセスする」には、ステップ1-1で作成したデバイスからアップロードした顔画像を保存するS3バケット名が必要です。
  ステップ2-1-1で作成した「コレクションに追加する顔の画像をアップロードするためのS3バケット」ではありませんので注意しましょう。*
![2-2-2_5](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_0.png)
![2-2-2_6](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step2/2-2-2_%E7%A2%BA%E8%AA%8D.png)


### 2-2-3. Pythonの関数コードを作成する

Lambdaが実行するPythonコードを作成します。

- Lambdaの関数画面に戻ってください

- 「関数コード」欄のヘッダー部の右端に「ハンドラ」として `lambda_function.lambda_handler`がデフォルトで指定されています。
  これは、当Lambdaが呼び出された際に実行される関数が `lambda_function.py`の中の`lambda_handler`という関数だという意味です。

- サンプルプログラムは[こちら](https://github.com/IoTkyoto/iot-handson-zybo-and-aws/blob/master/step2/lambda_authentication.py)の `lambda_authentication.py`をご確認ください。

- サンプルプログラムの内容をコピーし、関数コード欄にペーストしてください

- コードの13行目の以下の部分の「`{collection_id}`」を2-1-5で作成したコレクション名（例：`yamada-authentication-collection`）に変更してください

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

### 2-2-4. Lambdaのテストを実行する

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
      "threshold": 60
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


## 2-5. 顔認証を行うAPIからのレスポンスを利用し、ログ蓄積用のデータを形成する

ステップ2-4では、 `print()`関数を使い、コンソールにAPIレスポンスを表示しました。
しかし、APIレスポンスのデータ構造は複雑かつ、次のステップ5でのAWS Athena（以下、Athena）とAWS QuickSight（以下、QuickSight）を利用した可視化に不要な情報が多く含まれています。
ここでは、APIから受け取った今回のデータを次のステップで利用しやすい形に整形します。

- 具体的には以下のような操作を行います：

    - データの階層構造をフラットにし、配列[]の中に人数分の辞書型{}を格納する形にする
    - マッチした顔があるかどうかについて、認証データとは別にboolean値を返す
    - 認証データに、デバイスIDやマッチした顔の有無、判定に利用された顔画像ファイル名といったデータを追加する
    - 顔の座標やHTTPヘッダー情報など、可視化に不要なデータ部分を削ぎ落とす

- AthenaとQuickSightの公式ドキュメントには、それぞれ対応しているデータ構造が明記されていますので、以下をご確認ください。
    - [Athenaでサポートされるデータ型](https://docs.aws.amazon.com/ja_jp/athena/latest/ug/data-types.html)
    - [Quicksightのデータソースの制限](https://docs.aws.amazon.com/ja_jp/quicksight/latest/user/data-source-limits.html)

- 今回はGitHub上にデータ整形プログラムを用意しましたので、下記の手順でご使用ください。

### 2-5-1. データフォーマット用のPythonプログラムをダウンロードし、デバイス側に移す

以下のリポジトリをcloneし、その中の `scripts`というディレクトリを開いてください。
https://github.com/IoTkyoto/iot-handson-zybo-and-aws

### 2-5-2. `scripts`の中のPythonファイル `rekognition_data_formatter.py`を、ステップ2-4-1で作成したプログラムと同じ階層に移動させる

ステップ2-4-1で作成したPythonプログラムは、顔認証を行うWeb APIにアクセスするものです（例： `execute_authentication_api.py`）。

### 2-5-3. ステップ2-4-1で作成したプログラムの中で、`rekognition_data_formatter.py`をimportするよう追記する

- ステップ2-4-1で作成したプログラム（例： `execute_authentication_api.py`）にデータフォーマット処理を追加していきます。
- サンプルプログラムの12行目のimport文のコメントを外してください。
  ファイルをimportする場合は `.py`の拡張子まで書く必要はありませんのでご注意ください。

```python:import文
import rekognition_data_formatter
```

### 2-5-4. 顔認証APIのレスポンスをフォーマットする

- importした `rekognition_data_formatter`の中の`format_auth_log_data()`という関数にAPIレスポンスを渡し、加工させましょう。
- サンプルプログラムの105行目〜106行目の呼び出し文のコメントを外してください。

```python:execute_authentication_api.py
# 2-5-4で使用するAPIレスポンスの加工処理
response_json = json.loads(response)
format_result, format_data = rekognition_data_formatter.format_auth_log_data(json.dumps(response_json['payloads']), self.file_name)
```
#### データフォーマット機能の解説

**・rekognition_data_formatterのふるまい**
`rekognition_data_formatter`の中にある関数 `format_auth_log_data()`は、第1引数で与えられたJSON形式のデータを加工します。
加工に成功した場合、認証された人数分のデータのJSONを配列で返します。データの加工に失敗した場合、空配列を返します。
また、認証に成功したかどうかも最初の返り値として返します。

**・rekognition_data_formatterが期待する引数**

- 第1引数: JSON形式の、APIレスポンスを格納した変数（例： `json.dumps(payloads)`）
- 第2引数: ステップ2-4-1のファイルで第2引数に指定した画像ファイル名（例： `image01-20190731070707.jpg`）

**・rekognition_data_formatterの呼び出し方**
呼び出し方の詳細な例はサンプルプログラムをご参考ください([/scripts/test_rekognition_data_formatter.py](https://github.com/IoTkyoto/iot-handson-zybo-and-aws/blob/master/scripts/test_rekognition_data_formatter.py))。
この`test_rekognition_data_formatter.py`を実行すると、コード内に記述されたサンプルデータがフォーマットされて出力されます。
また、ステップ2-5-5で追記する`create_auth_log.log`というログファイルが出力されるようになっています。

```python:呼び出し例
rekognition_data_formatter.format_auth_log_data(json.dumps(payloads), `image01-20190731070707.jpg`)
```

**・rekognition_data_formatterが返す値**   
この`rekognition_data_formatter.format_auth_log_data()`の挙動は以下の通りです。
最初にboolean値で `True/False`を返すことで、ドアの開閉を行うかどうかの判定基準を与えています。

- マッチする顔があった場合：

```python
return True, [{加工済データ}x人数分]
```

- マッチする顔がなかった場合：

```python
return False, [加工済みデータ]
```

- 顔の認証を行なっていたかどうかに関わらず、データの加工処理に失敗した場合：

```python
return False, [空配列]
```

### 2-5-5. ログファイル出力をさせる

- ドア開閉プログラムにデータを渡す為に、`rekognition_data_formatter`の返り値をログファイルに出力させるコードを追記しましょう。
- サンプルプログラムの85行目~87行目、109行目〜110行目のコメントアウトを外してください。
- 「`create_auth_log.log`」というファイルに認証結果が書き込まれます。

```python:execute_authentication_api.py

def write_log(self, format_result, format_data):
   with open('create_auth_log.log', 'w') as f:
      f.write(str(format_result) + ',\n' + json.dumps(format_data))

・・・（中略）・・・

# 2-5-5で使うログ出力
if format_data != None:
   self.write_log(format_result, format_data)
```
#### 「create_auth_log.log」のデータ内容
- １行目：認証結果（True/False）
- ２行目：人数分の結果データ

### 2-5-6. `format_auth_log_data()`からの返り値によって処理を分岐させる

- `rekognition_data_formatter.format_auth_log_data()`の返り値が空配列でなければ、ステップ4で作成予定のログ送信プログラムに引数として渡す予定です。
- ただし、ステップ4のプログラムはまだ作成していないので、返り値が空配列かどうかの判定をif文で分岐させ、このステップではコメントアウトしておきましょう。

- サンプルプログラム81行目〜83行目、112行目~114行目のコメントアウトは**外さない**でください。

```python:execute_authentication_api.py
# def call_pub_auth_log_data(self, format_data):
#    for data in format_data:
#        subprocess.call(["python3", PUB_AUTH_LOG_PATH, json.dumps(data)])

・・・（中略）・・・

# step4の関数を呼び出す処理
# if format_data != []:
#    self.call_pub_auth_log_data(format_data)
```

