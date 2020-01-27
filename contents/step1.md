# ステップ1. 顔認識用のコレクションを作成する（スマートフォンとAWSサービスを用いた画像認識サービスの構築する）

*当コンテンツは、エッジデバイスとしてスマートフォン、クラウドサービスとしてAWSを利用し、エッジデバイスとクラウド間とのデータ連携とAWSサービスを利用した画像認識を体験し、IoT/画像認識システムの基礎的な技術の習得を目指す方向けのハンズオン(体験学習)コンテンツ「[スマートフォンとAWSサービスを用いた画像認識サービスの構築する](https://qiita.com/kyoso_bizdev/private/e5c252f08de019ab8a1b)」の一部です。*

# ステップ1. 顔認識用のコレクションを作成する

![ステップ1アーキテクチャ図](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/architecture_step1.png)

ステップ1では、画像に写っている人物を特定するために必要なコレクションを作成します。
AWS Rekognitionサービスでは、コレクションの情報を使って、画像内に誰が写っているのかを特定する機能があります。

まずは、画像のアップロード先として「[**Amazon S3（以下、S3）**](https://aws.amazon.com/jp/s3)」にバケットを作成し、登録したい人物が１人で写っている画像をAWSコンソールからアップロードします。

AWSのCLI(コマンド・ライン・インターフェース)ツールを使って、「**[Amazon Rekognition（以下、Rekognition）](https://aws.amazon.com/jp/rekognition/)**」の「コレクション」を作成し、認識対象となる顔を登録します。

---

### 目的

- AWSコンソールからクラウドにファイルをアップロードする
- AWS CLIの使い方を学ぶ

### 概要

- AWSコンソールからS3のバケットを作成し画像をアップロードする
- AWS CLI用のユーザーを作成する
- AWS CLIでRekognitionのコレクションを作成し画像を登録する

---

### ＜Amazon S3とは？＞

Amazon Simple Storage Service（Amazon S3）は、AWSによって提供されるクラウド型のオブジェクトストレージサービスです。容量無制限・高耐久性と低コストが大きな特徴です。

- 容量無制限
- [従量課金制](https://aws.amazon.com/jp/s3/pricing)
    - ユースケースに応じたさまざまなストレージクラスが存在している（IA,1ゾーンIA,Glacier etc）
    - 適したストレージクラスを使用することでコスト最適化が可能
- 高耐久性（99.999999999%）
    - 自動的に３箇所以上のAZ(アベイラビリティゾーン)に冗長に保存される
- バケット単位、オブジェクト単位の詳細なアクセス権限の設定が可能
- 保存期間を設定したライフサイクル設定が可能
- ファイルの世代管理が可能

より詳しく知りたい場合は[公式サイト](https://aws.amazon.com/jp/s3/)をご確認ください。

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

### ＜Amazon Rekognitionとは？＞

Amazon Rekognitionは、ディープラーニング技術を利用したフルマネージド型の画像認識サービスです。
画像や動画を対象に、画像のシーンやアクティビティの検出、顔認識、有名人の検出、顔の分析、テキスト抽出といった機能を提供します。
Rekognition APIに対象の画像を登録・送信するだけで、これらの機能を自身のアプリケーションに簡単に組み込み利用することが可能です。

- Amazon Rekognition Imageでは以下の機能が利用可能
    - 物体とシーンの検出
    - 顔認識
    - 顔分析
    - 顔の比較
    - 危険画像の検出
    - 有名人の認識
    - 画像内のテキスト検出
- Amazon Rekognition Videoでは以下の機能が利用可能
    - ストリーミングビデオのリアルタイム解析
    - 人物の識別と追跡
    - 顔認識
    - 顔分析
    - 物体、シーン、動作の検出
    - 不適切な動画の検出
    - 有名人の認識

より詳しく知りたい場合は[公式サイト](https://aws.amazon.com/jp/rekognition/)をご確認ください。

### ＜Amazon Rekognitionでの顔認識＞

顔認識を行うためにAmazon Rekognitionの機能のひとつである `SearchFacesByImage` という機能を使います。
Amazon Rekognitionでは、検出した顔に関する情報を `コレクション` というサーバー側のコンテナに保存できます
コレクションにはイメージが格納されているのではなく、顔ごとに顔の特徴を特徴ベクトルに抽出し、その特徴ベクトルが保存されています。
コレクションに保存された顔の情報を使用して、イメージ、保存済みビデオ、およびストリーミングビデオ内の既知の顔を検索することができます。
また、コレクション内の画像にタグをつけて「コレクションの中に登録されている顔であれば、登録した顔画像のタグを返す」といった使い方ができます。

詳細は、公式ドキュメント「[コレクション内での顔の検索](https://docs.aws.amazon.com/ja_jp/rekognition/latest/dg/collections.html)」をご確認ください。

---

## 1-1. コレクションに登録する画像をアップロードするためのS3バケットを作成

この項目ではAWSのS3というサービスを用いて、コレクションに登録するための画像の保存先となる「バケット」を作成していきます。
以下の手順でS3のバケットを用意します。

---

### ＜S3バケットとは？＞

Amazon S3に格納されるすべてのオブジェクト(ファイル)は、バケット（バケツ）と呼ばれる入れ物の中に存在します。
バケットの用途には、Amazon S3の最上位の名前空間を形成する、ストレージとデータ転送の課金アカウントを特定する、アクセスコントロールに使用する、使用状況レポートの集計単位として使用するなど、さまざまなものがあります。
もっとも重要な役割は「オブジェクトにたいして名前空間を提供する」ことです。
名前空間はすべてのAWSアカウントによって共有されますので、グローバルに一意である必要があります。
https://docs.aws.amazon.com/ja_jp/AmazonS3/latest/dev/UsingBucket.html

---

### 1-1-1. AWSのコンソール画面で「S3」を検索・選択し[バケットを作成する]をクリックする

![1-1-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-1-1_1.png)

![1-1-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-1-1_2.png)

### 1-1-2. バケット名を入力し[次へ]をクリックする

- バケット名：任意の名称（例：yamada-rekognition-collection-source）
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

### 1-1-3. 「オプションの設定」は何も設定せずに[次へ]をクリックする

今回はオプションの設定は使用しませんので、何もチェックをつけずに「次へ」をクリックしてください。

![1-1-3](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-1-3_1.png)

---

### ＜バージョニングとは？＞

バージョニングとは、同じバケット内でオブジェクトの複数のバージョンを保持する手段です。
バージョニングの設定をONにすることで、Amazon S3バケットに格納されたあらゆるオブジェクトのあらゆるバージョンを格納、取得、復元することができます。
オブジェクトを誤って削除した場合でも復元することが可能です。
https://docs.aws.amazon.com/ja_jp/AmazonS3/latest/dev/Versioning.html

### ＜サーバーアクセスのログ記録とは？＞

サーバーアクセスのログ記録をONにすると、バケットに対するリクエストの詳細が記録されます。
アクセスログのレコードごとに1つのアクセスリクエストの詳細として、リクエスタ、バケット名、リクエスト時刻、リクエストアクション、レスポンスのステータス、エラーコード (存在する場合) などの情報が取り込まれます。
https://docs.aws.amazon.com/ja_jp/AmazonS3/latest/dev/ServerLogs.html

---

### 1-1-4. 「アクセス許可の設定」を確認し[次へ]をクリックする

アクセス許可の設定では、S3バケットに対してアクセスできる権限を指定します。
「**パブリックアクセスをすべてブロック**」にチェックが入っているかを確認してください。

**【注意】 S3バケットのパブリックアクセスについて**
「パブリックアクセスが有効」な状態のS3バケットは、世界中の人々に公開されている状態となります。
S3バケットのパブリックアクセスが原因となった顧客情報の漏洩などの事件も発生しておりますので、アクセス権限の設定はお気をつけください。
![1-1-4](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-1-4_1.png)


### 1-1-5. 確認画面に表示されている内容を確認し[バケットを作成]をクリックする

バケットの作成リージョンが「アジアパシフィック（東京）」になっていることや、パブリックアクセスをブロックするようになっていることを確かめてからバケットを作成します。

![1-1-5](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-1-5_1.png)


## 1-2. S3バケットに画像をアップロードする

作成したバケットに、コレクションに登録したい人物の顔が写った画像をアップロードします。

- アップロードの作業に移る前に、下記注意事項をご確認ください。
  - **Rekognitionで利用できる画像の制限**
  Rekognitionに利用できる画像には制限がありますので、画像をアップロードする前にご確認ください。
  https://docs.aws.amazon.com/ja_jp/rekognition/latest/dg/limits.html
  - **画像に写っている顔の数**
  後述のRekognitionのコレクションへの顔の登録の性質から、画像に写っている顔は、登録したい人一人分の顔が写ったものを利用ください。

### 1-2-1. 対象のバケットを検索し選択する

- バケット検索欄にステップ1-1-5で作成したバケット名の一部を入力する（例：yamada）



- 対象のバケット名をクリックする


### 1-2-2. 対象画像をアップロードする

- アップロード画面に顔認識のベースとなる画像をドロップ


- オプションは何も指定せずに「アップロード」をクリック


- アップロードに成功した場合、画像ファイルがバケット内にリストで表示される


### 1-3. CLI操作用のユーザポリシーを作成する

現時点(2019/12/01時点)では、AWSのコンソール画面からRekognitionのコレクションは作成できないため、ローカルPCからAWS CLIを使用してコレクションを作成する必要があります。

お手元のパソコンでAWS CLIを利用するためには、必要な権限（**[ポリシー](https://docs.aws.amazon.com/ja_jp/IAM/latest/UserGuide/access_policies.html)**）を与えた「**[IAMユーザー](https://aws.amazon.com/jp/iam/)**」を作成する必要があります。
CLIからアクセスできるAWSサービス・処理内容・バケットを制限することでアクセス権限を最小限にし、セキュリティレベルを高めます。

まずは、今回の作業に必要な最低限の権限（**[ポリシー](https://docs.aws.amazon.com/ja_jp/IAM/latest/UserGuide/access_policies.html)**）として、以下の２種類の権限を持たせたポリシーを作成します。

- Step1-1で作成したS3バケットからオブジェクトを取得する
- Rekognitionでコレクションを扱う

*※ ローカルPCのAWS CLIにAdmin権限を付与済みであれば、当対応は不要です。*

---

### ＜IAMとは？＞
AWS Identity and Access Management (IAM) は、AWSのサービスやリソースへのアクセスを安全に管理するためのサービスです。
IAMを使用することで、AWSのユーザーとグループを作成および管理し、アクセス権を使用して AWSリソースへのアクセスを許可および拒否できます。
権限管理は非常に重要な部分ですので[IAMのベストプラクティス](https://docs.aws.amazon.com/ja_jp/IAM/latest/UserGuide/best-practices.html)をご確認いただく事を推奨します。

より詳しく知りたい場合は[公式サイト](https://aws.amazon.com/jp/iam/)をご確認ください。

### <Policyとは？>
AWSのIAMサービスでは、各AWSサービスへの操作をアクセス制御するために「ポリシー」という概念があります。 
ポリシーは、「誰が」「どのAWSサービスの」「どのリソースに対して」「どんな操作を」「許可する(許可しない)」、といったことをJSON形式で記述したものです。
作成したポリシーをユーザー（IAMユーザー、IAMグループ、IAMロール）や、AWSリソースに関連づけることで、アクセス制御を実現しています。

より詳しく知りたい場合は[公式サイト](https://docs.aws.amazon.com/ja_jp/IAM/latest/UserGuide/access_policies.html)をご確認ください。

---

### 1-3-1. AWSのコンソール画面で「IAM」を検索・選択し[ポリシー] -> [ポリシーの作成]をクリックする
IAMのポリシーでアクセス権限を設定し、これをユーザーにアタッチすることでユーザーにアクセス権限が付与されます。

- AWSサービス
![1-3-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-3-1_1.png)
![1-3-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-3-1_2.png)

### 1-3-2. ビジュアルエディタでサービス・アクション・リソースを設定する

ビジュアルエディタもしくはJSONでの記述により、アクセス権限をカスタムで作成できます。
ここではビジュアルエディタでの設定方法に沿って説明します。

#### 1-3-2-1. サービスを選択する

まずは、どのAWSサービスに対して権限を設定するかを選択します。

サービス欄の「`サービスの選択`」をクリックします。
![1-3-2-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-3-2-1_1.png)

サービスの検索ボックスに「`S3`」と入力して、下に表示されたサービスの候補から「`S3`」をクリックします。
![1-3-2-1_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-3-2-1_2.png)

#### 1-3-2-2. アクションを選択する

選択したS3サービスのどのアクションに権限を設定するかを選択します。

アクセスレベル欄の「`読み込み`」の「▶︎」をクリックし、「`GetObject`」にチェックを付けます。
![1-3-2-2_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-3-2-2_1.png)

#### 1-3-2-3. リソースを選択する

選択したS3サービスのPutObjectアクションに対してリソースの制限を設けます。

リソース欄の「▶︎」をクリックし、「`指定`」にチェックを付け、object欄の「`ARNの追加`」をクリックします。
![1-3-2-3_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-3-2-3_1.png)

ARNの追加ポップアップ画面に以下の情報を入力し「`追加`」をクリックします。
- Bucket name
    - Step1-1で作成したS3バケット名
    （例：yamada-rekognition-collection-source）
- Object name
    - 「`すべて`」にチェック付与

![1-3-2-3_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-3-2-3_2.png)

**【参考】 ARNとは**
[ARN](https://docs.aws.amazon.com/ja_jp/general/latest/gr/aws-arns-and-namespaces.html)とは *Amazon Resource Name* の略で、AWSのサービスやサービス内で作成したリソースを一意に識別するための特殊な表記のことです。
ARNの表記方法はAWSサービスごとに異なります。
S3の「オブジェクト」とは、S3バケット内のすべてのアイテムを指します。
また


#### 1-3-2-4. S3用のポリシー設定内容を確認する

S3サービスに対するポリシーの内容が以下の画面通りとなっていることを確認し、「`さらにアクセス許可を追加する`」をクリックします。
![1-3-2-4_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-3-2-4_1.png)

#### 1-3-2-5. Rekognitionでコレクションを扱うためのポリシーを作成する

今度は、1-3-2-1 ~ 1-3-2-3までの手順にしたがって、Rekognitionのサービスを利用するための権限を追加します。

- サービス： `Rekognition`
- アクション：
	- [読み込み] `ListCollections`、 `ListFaces`、 `SearchFacesByImage
`
	- [書き込み] `CreateCollection`、 `IndexFaces`、 `DeleteCollection`、 `DeleteFaces`
- リソース：すべてのリソース

#### 1-3-2-6. Rekognition用のポリシー設定内容を確認する

Rekognitionサービスに対するポリシーの内容が以下の画面通りとなっていることを確認し、「`ポリシーの確認`」をクリックします。
![1-3-2-6_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-3-2-6_1.png)


#### 1-3-2-7. ポリシーに名前をつけて[ポリシーの作成]をクリックする

ポリシーの作成に必要な情報を入力・確認し、「`ポリシーの作成`」をクリックします。

- 名前：任意の名称（例：yamada_local_rekognition_operation_policy）
- 説明：任意（例：Policy for Rekognition collection operations for AWS CLI on local PC）
- 概要：以下の画像の通りであること
![1-3-2-7_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-3-2-7_1.png)

**【参考】ポリシーをJSON形式で登録する**
- 以下の画像のように、JSON形式でポリシーを直接記述して登録することも可能です。
![1-3-2-7_2](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-3-2-7_2.png)

## 1-4. CLI操作用のIAMユーザーを作成する

AWS CLI用のIAMユーザーを作成し、ステップ1-3で作成したポリシーを関連付けします。

### 1-4-1. ユーザーの追加を選択する

IAM画面のサイドメニュー欄から「`ユーザー`」をクリックし、ユーザ一覧上部の「`ユーザーを追加`」をクリックする。

![1-4-1_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-4-1_1.png)

### 1-4-2. 作成するユーザーの情報を入力する

以下の情報を入力し、「`次のステップ:アクセス権限`」をクリックします。
- ユーザー名：任意の名称（例：device_user）
- プログラムによるアクセス：チェック
- AWSマネジメントコンソールへのアクセス：チェックなし
![1-4-2_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-4-2_1.png)

*このステップで作成するユーザはデバイスからAWS SDK経由のプログラムからアクセスするためのユーザとなりますので、AWSコンソールへのログインは不要としプログラムによるアクセスのみ有効としましょう。*

### 1-4-3. ポリシーを関連づける

設定するポリシーを指定し、「`次のステップ:タグ`」をクリックします。

- アクセス許可の設定欄の「既存のポリシーを直接アタッチ」をクリック
- ステップ1-3で作成したポリシーを検索しチェックを付与
（例：yamada_local_rekognition_operation_policy）
![1-4-3_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-4-3_1.png)

### 1-4-4. タグを設定する

今回のケースではタグを使用しないため、何も入力せずに「`次のステップ:確認`」をクリックします。
![1-4-4_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-4-4_1.png)

#### ＜タグとは？＞
タグとは、AWSリソースを整理するためのメタデータとして使用されるキーと値のペア値のことです。
タグを使用して[リソースグループ](https://docs.aws.amazon.com/ja_jp/ARG/latest/userguide/welcome.html)を作成すると、複数のリージョンやサービスをまたいでプロジェクト別にAWSリソースを視覚化できます。
タグを使用してAWSの請求を整理して視覚化する方法については「[コスト配分タグの使用](https://docs.aws.amazon.com/ja_jp/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html)」を参照してください。


### 1-4-5. IAMユーザーの登録内容を確認する

確認画面で表示されている内容に問題がなければ、「`ユーザーの作成`」をクリックします。
![1-4-5_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-4-5_1.png)

### 1-4-6. [.csvのダウンロード]をクリックする

AWSにコマンドラインからアクセスするための認証（クレデンシャル）情報として、アクセスキーとシークレットアクセスキーが生成されます。
次のステップで利用しますのでダウンロードしておきましょう。
![1-4-6_1](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step1/1-4-6_1.png)

## 1-5. AWS CLIに認証情報を登録する

作成した認証(クレデンシャル)情報を、ローカルPCのAWS CLIに登録します。

### 1-5-1. AWS Configureを登録する

ローカルPCのコマンドラインから、認証情報を設定してください。
（Windowsの場合はコマンドプロンプト、Macの場合はターミナルを使用）
AWS CLIは `aws`コマンドで動作しますので、以下のコマンドを実行してください。

```shell:認証情報の設定
$ aws configure
```

その後、 アクセスキー、シークレットアクセスキー、デフォルトリージョン、デフォルト出力フォーマットの順に情報を入力してください。

- 【アクセスキー】 `AWS Access Key ID :` 
1−4−6でダウンロードしたCSVファイルのAccessKeyを設定してください
- 【シークレットキー】 `AWS Secret Access Key :`
1−4−6でダウンロードしたCSVファイルのSecretKeyを設定してください
- 【デフォルトリージョン】 `Default region name :`
東京リージョンを意味する「 `ap-northeast-1`」を設定してください
- 【デフォルト出力フォーマット】 `Default output format :`
`json`を設定してください

**【注意】 デフォルトの登録について**
この時、デフォルトリージョンや出力フォーマットを大文字で入力するなどのタイプミスをすると、この後のサービスへのアクセスがうまくできなかったり、コマンドラインへの出力がうまくされなくなります。
上記の通りに入力するようご注意ください。

### 1-5-2. 正しく接続出来ることを確認する

AWS CLIに正しく認証情報が登録され、対象のAWS環境に接続出来ることを確認します。

先ほどS3にバケットを作成しましたので、以下のコマンドでS3のバケット一覧を表示してみてください。

```shell:S3バケット一覧の表示
$ aws s3 list
```

正しく認証情報が登録出来ている場合は、以下のように1-1で作成したバケットが表示されます。

```shell:S3バケット一覧
$ 2019-11-01 11:12:34 yamada-rekognition-collection-source
```


## 1-6. コレクションを作成する

顔認証サービスを利用するために、認証の対象となる顔データの登録先となるコレクションを作成します。
コレクションには、 `--collection-id`パラメーターで名前をつける必要があります。
使用目的が分かるようなコレクション名をつけましょう。
（例：yamada-authentication-collection）

### 1-6-1. コレクションを作成する

- 以下のコマンドを実行しコレクションを作成してください
  コマンドの詳細は、公式ドキュメント「[コレクションの作成](https://docs.aws.amazon.com/ja_jp/rekognition/latest/dg/create-collection-procedure.html)」をご確認ください。

```shell:実行コマンド例
# collection-id の引数は任意のコレクション名にしてください
$ aws rekognition create-collection --collection-id "yamada-authentication-collection"
```

- 出力結果が以下のようにStatusCodeが200となれば、コレクションが正常に作成できています

```shell:実行結果
$ aws rekognition create-collection --collection-id "yamada-authentication-collection"
{
    "StatusCode": 200,
    "CollectionArn": "aws:rekognition:ap-northeast-1:XXXXXXXXXXXX:collection/yamada-authentication-collection",
    "FaceModelVersion": "4.0"
}
```

### 1-6-2. コレクションの作成を確認する

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

## 1−7. コレクションに顔を登録する

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

## 1-8. コレクションをテストする

ステップ1-1で作成したバケットとアップロードした画像を利用して、コレクションに登録した顔とマッチするかテストします。コレクションに登録した顔のデータと、そのデータの元となる画像を比較するため、マッチ率は100%に限りなく近い数値となります。

- 以下のコマンドを実行し、指定した画像の中にコレクション内の顔と一致する顔があるか確認します

```shell:実行コマンド例
$ aws rekognition search-faces-by-image \
--image '{"S3Object":{"Bucket":"yamada-rekognition-collection-source","Name":"Taro_Yamada.jpg"}}' \
--collection-id "yamada-authentication-collection"
```

- **パラメーターの説明**
  コマンドの詳細は、[こちら](https://docs.aws.amazon.com/ja_jp/rekognition/latest/dg/search-face-with-image-procedure.html)の公式ドキュメントをご参考ください。

  - `--image`
      - パラメーター内の `"Bucket"`属性の値には、ステップ1-1で作成したバケット名、 
      - `"Name"`属性の値には、ステップ1-2でアップロードした画像ファイル名を、それぞれ入力します

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
---

### 次のステップへ進んでください
