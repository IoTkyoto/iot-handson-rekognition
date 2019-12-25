---
title: ステップ3. 顔画像分析結果を取得するWeb APIを作成する（ZyboとAWSサービスを用いてデバイスとクラウドの双方向通信とデータの可視化・分析を行う）
tags: IoT AWS zybo ubuntu16.04 Python3
author: kyoso_bizdev
slide: false
---
*当記事は、エッジデバイスとしてZybo(OS:ubuntu)を、クラウドサービスとしてAWSを利用し、エッジデバイスとクラウド間との連携を本格的に体験し、IoTシステムの基礎的な技術の習得を目指す方向けのハンズオンコンテンツ記事「[ZyboとAWSサービスを用いてデバイスとクラウドの双方向通信とデータの可視化・分析を行う](https://qiita.com/kyoso_bizdev/private/e5c252f08de019ab8a1b)」の一部です。*
# ステップ3. 顔画像分析結果を取得するWeb APIを作成する

![ステップ3アーキテクチャ図](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/architecture_step3.png)

ステップ2の応用として、「S3バケットの画像を指定すると、その画像に写る顔の特徴を分析するAPI」を作成し、最後はデバイスからAPIにアクセスします。
簡単なヒントを書いておりますので、このヒントとステップ2を参考に実装してみましょう。

- 顔の分析を行うために、Amazon Rekognitionの機能のひとつである `DetectFaces` という機能を使います
- 顔の分析では、Rekognitionのコレクション作成は必要ない為、ステップ2-1に相当する手順はありません
- APIは、ステップ2-3で作成したものをベースにして新しいリソースを作成しましょう
- Lambdaに引数としてS3バケット名などの値を渡すため、メソッドはPOSTにしましょう

---

#### 目的

- AWSの画像認識機能を知る
- 1つ前のステップで実行したことを参考に自分でWeb APIを作成してみる

#### 概要

- 顔分析用Web APIを作成し、デバイスから利用する

---

### ＜Amazon Rekognitionでの顔分析＞

Amazon Rekognitionでは、イメージ内やビデオ内の顔を検出し、顔の検出場所、目の位置などの顔のランドマーク、楽しさや悲しさなどの感情の検出に関する情報を取得できます。
イメージ内の顔を検出し、顔の属性を分析して、イメージ内で検出した顔と顔属性の信頼スコア(%)を返します。
たとえば、ある画像を分析した結果として、90%の信頼性スコアで「男性」、85%の信頼性スコアで「笑顔」という情報を返します。
詳細は公式ドキュメント「[顔の検出と分析](https://docs.aws.amazon.com/ja_jp/rekognition/latest/dg/faces.html)」をご確認ください。


今回のステップではイメージ内の顔の分析を行うために `DetectFaces` という機能を使います。
使用方法は公式ドキュメント「[イメージ内の顔の検出](https://docs.aws.amazon.com/ja_jp/rekognition/latest/dg/faces-detect-images.html)」をご確認ください。


## 3-1. AWS Lambdaで関数を新規作成

指定したS3バケット内の画像に写っている顔がどのような顔か、Rekognitionを用いた分析結果をリターン値として返すLambda関数部分を作成します。

ステップ2-2-1を参考に、新たなLambda関数を作成しましょう。

#### LambdaのIAMロールについて
Lambdaに必要な権限(Rekognitionに関する部分)が前回と異なります。
**上述の `DetectFaces`のオペレーションの権限が必要となりますので、ポリシー作成時に気をつけましょう。**
なお、今回はコレクションが必要ない為、リソースの指定も必要ありません。
S3へのアクセス権限については、ステップ1-1で作成した顔認証のターゲット画像を保存するためのバケットをそのまま利用するので、ステップ2-2-2と同じです。

- RekognitionのDetectFacesへのアクセスや、顔認証のターゲットとなる画像にアクセスできるように、以下の権限をインラインポリシーとして追加し、任意の名前で登録しましょう
  - **Rekognitionのコレクションにアクセスする**
    - サービス： `Rekognition`
    - アクション：[読み込み] `DetectFaces`
    - リソース：指定不要
  - **顔認証のターゲットなる画像データにアクセスする**
    - サービス： `S3`
    - アクション：[読み込み] `GetObject`
    - リソース：[指定]を選択し、object欄の[ARNを指定]をクリック。ステップ1-1で作成したバケット名（例： `yamada-target-images-bucket`）を入力し、Objectは[すべて]にチェック

## 3-2. LambdaにPythonの関数コードを実装

ステップ2-2-3を参考にLambdaのPythonコードを実装しましょう。

以下にコードの実装に最低限必要な要素を挙げています。後のステップに影響する実装もありますので、必ずご確認ください。

- サンプルプログラムは[こちら](https://github.com/IoTkyoto/iot-handson-zybo-and-aws/blob/master/step3/lambda_analysis.py)の `lambda_analysis.py`をご確認ください。

- サンプルプログラムの内容をコピーし、関数コード欄にペーストしてください

#### 作成プログラムの解説

- import一覧（例）

```python:lambda_function.py
import json                       # JSONフォーマットのデータを扱うために利用します
import boto3                      # AWSをPythonから操作するためのSDKのライブラリです
from datetime import datetime     # この関数を動かした（＝顔の認証を行なった）時間をtimestampとして作成するのに利用します
from botocore.exceptions import ClientError   # boto3実行時に発生する例外クラスです
```

- 今回APIが呼ばれる際のパラメーターに、以下のデータを受け取ることを想定して実装しましょう
	- `bucket_name`：認証を行いたい顔画像を保存しているS3バケット名
	- `file_name`：上で指定したS3バケットに保存されている、認証を行いたい顔画像ファイル名

- boto3 client `rekognition`のメソッド `detect_faces`を使用する
	- こちらのドキュメントを参考に実装してください
		- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.detect_faces
	- `Attributes`は指定した画像で分析しレスポンスとして受け取りたい内容を示します。`["DEFAULT"]`指定では今回欲しい情報が欠けていますので、今回は全ての値を意味する `["ALL"]`の利用を前提としています
		- 欲しい情報をカスタムでリスト指定することも可能ですが、この先のステップに影響が出ますので `["ALL"]`にしてください

- Lambdaの実行結果として返すレスポンスのボディとして、`'payloads'`という辞書型のデータを作成しましょう
	- 今回は `'payloads'`の中に `detect_faces`の戻り値（配列型）と `'timestamp'`属性を入れましょう
	- `detect_faces`の戻り値は配列型ですので、前回のように `update`メソッドを利用できません。 
	- 新たな辞書型 `'analysis'` を作成し、その中に入れてください
		- `payloads['analysis'] = data` （ `data`は`detect_faces`の戻り値を格納した変数）

- 作成完了後にはS3バケットに存在する画像をテストデータとしてテストを実施してみましょう

```json:テストイベント用JSONデータ例
{
  "body": {
    "bucket_name": "yamada-target-images-bucket",
    "file_name": "image01-20190731070707.jpg"
  }
}
```

## 3-3. Web APIを作成

ステップ2-3を参考にWeb APIを作成しましょう。

### ステップ2-3-1で作成したAPI Gatewayに新たなリソースとメソッドを追加しましょう
- `/` に対して新たに「リソースの作成」をしてください。（例：analyze）

![3-3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step3/3-3.png)

- 今回作成したAPIリソースにも、`POST`メソッドを追加しましょう
- また、こちらもAPIキーを必要とする設定にすることを忘れないようにしましょう
- 「/」を選択し「APIのデプロイ」をクリックし、前回のAPIと同じステージ「prod」にデプロイしましょう

ステップ2-3-6でデプロイしたステージを更新する形でデプロイすることで、使用量プランとAPIキーに、ステップ2-3-7で作成したものを引き続き適用できます。

- 最後に、ステップ2-3-8を参考に、cURLでAPIをテストしましょう。以下、ステップ2-3-8との相違点です
  - APIのリソース名は、2-3-2で作成したAPIのリソース名（例：analysis）に変更しましょう
　- 今回はデータに `threshold`が不要です

```shell:実行コマンド例
curl -X POST "https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prod/analysis" \
-H "X-Api-Key: xxxxxxxxxxxxxxxx" -H "Content-Type: application/json" \
-d "{\"file_name\":\"image01_20190808181200.jpg\",\"bucket_name\":\"yamada-target-images-bucket\"}"
```

- コマンドを実行すると、Lambda側で実装したレスポンスが返ってきます。

```shell:実行結果
curl -X POST "https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prod/analysis" \
-H "X-Api-Key: xxxxxxxxxxxxxxxx" -H "Content-Type: application/json"　\
-d "{\"file_name\":\"image01_20190808181200.jpg\",\"bucket_name\":\"yamada-target-images-bucket\"}"

{"msg": "[SUCCEEDED]Analysis done", "payloads": {"timestamp": "2019-08-19 02:40:47", 
"analysis": [{"BoundingBox": {"Width": 0.24594193696975708, "Height": 0.45506250858306885, "Left": 0.21459317207336426, 
"Top": 0.1758822500705719}, "AgeRange": {"Low": 17, "High": 29}, "Smile": {"Value": true, "Confidence": 98.37432861328125}, 
"Eyeglasses": {"Value": false, "Confidence": 99.78524780273438}, "Sunglasses": {"Value": false, "Confidence": 99.92851257324219}, 
"Gender": {"Value": "Male", "Confidence": 65.89674377441406}, "Beard": {"Value": false, "Confidence": 94.3515625}, 
"Mustache": {"Value": false, "Confidence": 99.3499526977539}, "EyesOpen": {"Value": true, "Confidence": 99.5592269897461}, 
"MouthOpen": {"Value": true, "Confidence": 96.93090057373047}, "Emotions": [{"Type": "DISGUSTED", 
"Confidence": 0.00844572950154543}, {"Type": "HAPPY", "Confidence": 99.76074981689453}, 
{"Type": "SAD", "Confidence": 0.029207248240709305}, {"Type": "SURPRISED", "Confidence": 0.0320408008992672}, 
{"Type": "FEAR", "Confidence": 0.03245721757411957}, {"Type": "CALM", "Confidence": 0.08961751312017441}, 
{"Type": "CONFUSED", "Confidence": 0.00938632246106863}, {"Type": "ANGRY", "Confidence": 0.03810255229473114}], 
・・・（省略）・・・
```

## 3-4. 顔分析を行うWeb APIにアクセスするプログラムを作成する

ステップ2-4を参考に、今回作成した顔分析のWeb APIにPOSTメソッドでアクセスするPythonプログラムを作成します。

Pythonプログラムはステップ2-4-1で作成したものをベースに実装し、必要に応じて修正してください。

今回は以下を引数に指定するプログラムを作成します。

- 第1引数：実行するPythonファイル（例: `execute_analysis_api.py`）
- 第2引数：ステップ1-1で作成したS3にアップロードした画像ファイル名（例: `image01_20190819104607.jpg`）
- 第3引数：ステップ1-1で作成したS3のバケット名（例: `yamada-target-images-bucket`）


```bash:実行コマンド
$ python3 execute_analysis_api.py image01_20190819104607.jpg yamada-target-images-bucket
```

プログラムに必要な要素はステップ2-4-1とほぼ同じです。
ただし、今回は引数に`threshold`を受け取りませんので、ご注意ください。

- サンプルプログラムは[こちら](https://github.com/IoTkyoto/iot-handson-zybo-and-aws/blob/master/step3/execute_analysis_api.py)の `execute_analysis_api.py`をご参考ください。
- サンプルプログラムの内容をコピーし、コード内の以下の部分を変更してください
    - 16行目「`API_KEY =  'xxxxxxxxxxxxxxxxxxx'`」 → 作成プログラムのAPIキーを参照
    - 18行目「`STAGE = 'xxxxxx'`」 → 作成ししたAPIをデプロイしたステージ名（例：prod）
    - 20行目「`API_ID = 'xxxxxx'`」 → 下記の「作成プログラムの解説」のAPIのエンドポイントの「`.execute-api.api-northeast-1.~`」の前の英数字部分
    - 24行目「`RESOURCE = 'xxxxxx'`」 → 作成したAPIのリソース名（例：analyze）

## 3-5. デバイスからプログラムでWeb APIを利用

ステップ2-4で行った手順を参考に、作成したプログラムを実行してみましょう。
Pythonプログラム実行後の出力を確認します。

```shell:実行結果
$ python3 execute_analysis_api.py image01_20190819104607.jpg yamada-target-images-bucket
{"msg": "[SUCCEEDED]Analysis done", "payloads": {"timestamp": "2019-08-19 02:40:47", 
"analysis": [{"BoundingBox": {"Width": 0.24594193696975708, "Height": 0.45506250858306885, "Left": 0.21459317207336426, 
"Top": 0.1758822500705719}, "AgeRange": {"Low": 17, "High": 29}, "Smile": {"Value": true, "Confidence": 98.37432861328125}, 
"Eyeglasses": {"Value": false, "Confidence": 99.78524780273438}, "Sunglasses": {"Value": false, "Confidence": 99.92851257324219}, 
"Gender": {"Value": "Male", "Confidence": 65.89674377441406}, "Beard": {"Value": false, "Confidence": 94.3515625}, 
"Mustache": {"Value": false, "Confidence": 99.3499526977539}, "EyesOpen": {"Value": true, "Confidence": 99.5592269897461}, 
"MouthOpen": {"Value": true, "Confidence": 96.93090057373047}, "Emotions": [{"Type": "DISGUSTED", 
"Confidence": 0.00844572950154543}, {"Type": "HAPPY", "Confidence": 99.76074981689453}, 
{"Type": "SAD", "Confidence": 0.029207248240709305}, {"Type": "SURPRISED", "Confidence": 0.0320408008992672}, 
{"Type": "FEAR", "Confidence": 0.03245721757411957}, {"Type": "CALM", "Confidence": 0.08961751312017441}, 
{"Type": "CONFUSED", "Confidence": 0.00938632246106863}, {"Type": "ANGRY", "Confidence": 0.03810255229473114}], 
・・・（省略）・・・
```

単体で実行に成功したあとは、`1-6. ステップ2, ステップ3で実装するプログラムをcallするコードを追記する`でコメントアウトして追記した部分の２９行目と93行目のコメントアウトを外し、ステップ1で実装したコードを実行しましょう。
これにより、デバイスから画像を投稿→顔分析の流れを検証することができます。

```python:upload_target_image.py_29行目93行目
# ステップ3で構築するプログラムのパス
EXECUTE_ANALYSIS_PATH = '../step3/execute_analysis_api.py'

・・・（中略）・・・

# ステップ3で構築するプログラムをcallする
subprocess.call(["python3", EXECUTE_ANALYSIS_PATH, relation_s3.filename, args[2]])
```

```shell:画像アップロードから画像認証・顔分析まで続けて実施
$ python3 upload_target_image.py picture/image01.jpg yamada-target-images-bucket
[succeeded!] upload file name: image01_20190819115508.jpg
{"msg": "[SUCCEEDED]Rekognition done", "payloads": {"timestamp": "2019-08-19 02:55:09", "SearchedFaceBoundingBox": {"Width": 0.
・・・（省略）・・・
```

## 3-6. 顔分析を行うAPIからのレスポンスを利用し、ログ蓄積用のデータを形成

ステップ2-5で行なったように、APIレスポンスのデータ整形を行いましょう。

- 具体的には以下のような操作を行います：

    - データの階層構造をフラットにし、配列[]の中に人数分の辞書型{}を格納する形にする
    - 顔の座標や分析結果の信頼度、HTTPヘッダー情報など、可視化に不要なデータ部分を削ぎ落とす


[こちら](https://github.com/IoTkyoto/iot-handson-zybo-and-aws/blob/master/step3/rekognition_data_formatter.py)のリポジトリの `scripts`というディレクトリ内にある `rekognition_data_formatter.py`の関数 `format_analysis_log_data()`を使用します。
利用するPythonファイルは前回と同じですが、関数名だけが前回と異なりますのでご注意ください。

- [サンプルプログラム](https://github.com/IoTkyoto/iot-handson-zybo-and-aws/blob/master/step3/execute_analysis_api.py#L26)では11行目と91行目〜93行目が該当箇所にあたります。

```python:execute_analysis_api.py_11行目
import rekognition_data_formatter
```

```python:execute_analysis_api.py_91行目〜93行目
# 3-6で使用するAPIレスポンスの加工処理
response_json = json.loads(response)
format_data = rekognition_data_formatter.format_analysis_log_data(json.dumps(response_json['payloads']))
```

**※Pythonは同じ階層のファイルしかimport出来ない為、`rekognition_data_formatter.py`は`execute_analysis_api.py`と同じディレクトリに作成してください**

---
### 実装内容
引数はAPIレスポンスのみです。前回同様、`json.dumps()`でデータをJSON形式に変換してから引数に指定してください。

**・rekognition_data_formatterが期待する引数**
`第1引数: JSON形式の、APIレスポンスを格納した変数（例： json.dumps(payloads)）`

**・rekognition_data_formatterの呼び出し方**

```python:execute_analysis_api.py
# 呼び出し例:
rekognition_data_formatter.format_analysis_log_data(json.dumps(payloads))
```

**・rekognition_data_formatterが返す値**
    
この`rekognition_data_formatter.format_analysis_log_data()`の挙動は以下の通りです。
今回はステップ2-5とは異なり、最初の戻り値に booleanの `True/False`はない為ご注意ください。

- 顔分析結果のデータの加工処理に成功した場合：

```python:rekognition_data_formatter.py
return [{加工済データ}x人数分]
```

- 失敗した場合：

```python:rekognition_data_formatter.py
return [空配列]
```
## 3-7. ステップ4の関数を呼び出す処理をコメントアウトで追記
`rekognition_data_formatter.format_analysis_log_data()`の戻り値が空配列でなければ、ステップ4で作成予定のログ送信プログラムに引数として渡す予定です。
ただし、ステップ4.のプログラムはまだ作成していないので、このステップではコメントアウトしておきましょう。

サンプルプログラム 28行目~29行目、72行目~74行目と95行目~97行目の**コメントアウトを外さずに**追記してください。

```python:execute_analysis_api.py_28行目~29行目
# step4で作成するログ送信用プログラムのパス
# PUB_ANALYSIS_LOG_PATH = '../step4/pub_analysis_log_data.py'

```

```python:execute_analysis_api.py_72行目~74行目
# def call_pub_analysis_log_data(self, format_data):
#      for data in format_data:
#           subprocess.call(["python3", PUB_ANALYSIS_LOG_PATH, json.dumps(data)])

```

```python:execute_analysis_api.py_95行目~97行目
# step4の関数を呼び出す処理
# if format_data != []:
#      self.call_pub_analysis_log_data(format_data)

```


