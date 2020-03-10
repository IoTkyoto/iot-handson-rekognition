# ステップ3. 顔画像分析結果を取得するWeb APIを作成する（スマートフォンとAWSサービスを用いた画像認識サービスの構築する）

*当コンテンツは、エッジデバイスとしてスマートフォン、クラウドサービスとしてAWSを利用し、エッジデバイスとクラウド間とのデータ連携とAWSサービスを利用した画像認識を体験し、IoT/画像認識システムの基礎的な技術の習得を目指す方向けのハンズオン(体験学習)コンテンツ「[スマートフォンとAWSサービスを用いた画像認識サービスの構築する](https://qiita.com/kyoso_bizdev/private/e5c252f08de019ab8a1b)」の一部です。*

# ステップ3. 顔画像分析結果を取得するWeb APIを作成する

![ステップ3アーキテクチャ図](https://s3.amazonaws.com/docs.iot.kyoto/img/Rekognition-Handson/step3/architecture_step3.png)

ステップ2の応用として、「画像をアップロードすると、その画像に写る顔の特徴を分析するAPI」を作成し、最後はデバイスからAPIにアクセスします。
簡単なヒントを書いておりますので、このヒントとステップ2を参考に実装してみましょう。

- 顔の分析を行うために、Amazon Rekognitionの機能のひとつである `DetectFaces` という機能を使います
- 顔の分析では、Rekognitionのコレクション作成は必要ない為、以下のようなコレクションに関する作業は必要ありません
  - Rekognitionのコレクションにアクセスするポリシーの作成（ステップ2-1-2）
  - Lambdaに渡す引数としての、コレクションに登録している顔との一致度(threshold)（ステップ2-1-3）
  - Lambda内でのコレクションIDの定義や、Rekognitionのメソッド利用時の引数指定（ステップ2-1-3）
- APIは、ステップ2-2で作成したものをベースにして新しいリソースを作成しましょう
- ステップ2と同じく、Lambdaに引数としてbase64の画像データを渡すため、APIのメソッドはPOSTにしましょう

---

#### 目的

- AWSの画像認識機能を知る
- 1つ前のステップで実行したことを参考に自分でWeb APIを作成してみる

#### 概要

- 顔分析用Web APIを作成し、デバイスからWeb APIを利用する

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

ステップ2-1-1を参考に、新たなLambda関数を作成しましょう。

#### LambdaのIAMロールについて

Lambdaに必要な権限(Rekognitionに関する部分)が前回と異なります。
**上述の `DetectFaces`のオペレーションの権限が必要となりますので、ポリシー作成時に気をつけましょう。**
なお、今回はコレクションが必要ない為、リソースの指定は必要ありません。

- RekognitionのDetectFacesメソッドにアクセスできるように、以下の権限をインラインポリシーとして追加し、任意の名前で登録しましょう
  - **Rekognitionのコレクションにアクセスする**
    - サービス： `Rekognition`
    - アクション：[読み込み] `DetectFaces`
    - リソース：指定不要

## 3-2. LambdaにPythonの関数コードを実装

ステップ2-1-3を参考にLambdaのPythonコードを実装しましょう。

以下にコードの実装に最低限必要な要素を挙げています。後のステップに影響する実装もありますので、必ずご確認ください。

- サンプルプログラムは[こちら](https://github.com/IoTkyoto/iot-handson-rekognition/blob/master/step2/lambda_analysis.py)の `lambda_analysis.py`をご確認ください。

- サンプルプログラムの内容をコピーし、関数コード欄にペーストしてください

#### 作成プログラムの解説

- import一覧（例）

```python:lambda_function.py
import json                       # JSONフォーマットのデータを扱うために利用します
import boto3                      # AWSをPythonから操作するためのSDKのライブラリです
from typing import Union, Tuple   # 変数や引数・返り値などの型定義に利用します
from datetime import datetime     # この関数を動かした（＝顔の認証を行なった）時間をtimestampとして作成するのに利用します
import botocore.exceptions        # boto3実行時に発生する例外クラスです
import base64                     # base64フォーマットの画像データをRekognitionが認識できる形に変換するのに利用します
```

- 今回APIが呼ばれる際のパラメーターに、以下のデータを受け取ることを想定して実装しましょう
  - `image_base64str`：認証を行いたい顔画像ファイル(pngもしくはjpeg)をbase64でエンコードしたデータ(文字列型)

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

- 作成完了後には、以下のjsonファイルの内容をテストデータとして利用し、テストを実施してみましょう

- テストデータは[こちら](https://github.com/IoTkyoto/iot-handson-rekognition/blob/master/step3/lambda_analysis_event_example.json)の `lambda_authentication_event_example.json`をご確認ください。

- テストデータの内容をコピーし、テストイベントのコード欄に貼り付けてください

## 3-3. Web APIを作成

ステップ2-2を参考にWeb APIを作成しましょう。

### ステップ2-3-1で作成したAPI Gatewayに新たなリソースとメソッドを追加しましょう
- `/` に対して新たに「リソースの作成」をしてください。（例：analyze）

![3-3](https://s3.amazonaws.com/docs.iot.kyoto/img/iot-handson-zybo-and-aws/step3/3-3.png)

- 今回作成したAPIリソースにも、`POST`メソッドを追加しましょう
- また、こちらもAPIキーを必要とする設定にすることを忘れないようにしましょう
- 「/」を選択し「APIのデプロイ」をクリックし、前回のAPIと同じステージ「prod」にデプロイしましょう

ステップ2-2-6でデプロイしたステージを更新する形でデプロイすることで、使用量プランとAPIキーに、ステップ2-2-7で作成したものを引き続き適用できます。

- 最後に、ステップ2-2-8を参考に、cURLでAPIをテストしましょう。

- shellファイルは[こちら](https://github.com/IoTkyoto/iot-handson-rekognition/blob/master/step2/curl_test_analysis_format.sh)の `curl_test_analysis_format.sh`をご確認ください。

- 以下、ステップ2-2-8との相違点です
  - APIのリソース名は、2-3-2で作成したAPIのリソース名（例：analysis）に変更しましょう
　- 今回はデータに `threshold`が不要です


- コマンドを実行すると、Lambda側で実装したレスポンスが返ってきます。

```shell:実行結果
sh curl_analysis_test_format.sh

{"msg": "[SUCCEEDED]Analysis done", "payloads": {"timestamp": "2019-08-19 01:40:17", 
"analysis": [{"BoundingBox": {"Width": 0.3842945396900177, "Height": 0.4907236397266388, "Left": 0.34415897727012634, 
"Top": 0.28372901678085327}, "AgeRange": {"Low": 21, "High": 33}, "Smile": {"Value": false, "Confidence": 58.52912521362305}, 
"Eyeglasses": {"Value": false, "Confidence": 99.91854858398438}, "Sunglasses": {"Value": false, "Confidence": 99.9820556640625}, 
"Gender": {"Value": "Male", "Confidence": 98.9040298461914}, "Beard": {"Value": false, "Confidence": 93.08826446533203}, 
"Mustache": {"Value": false, "Confidence": 99.42503356933594}, "EyesOpen": {"Value": true, "Confidence": 95.3335952758789}, 
"MouthOpen": {"Value": false, "Confidence": 98.8746109008789}, "Emotions": [{"Type": "SURPRISED", "Confidence": 0.25857076048851013}, 
{"Type": "CONFUSED", "Confidence": 0.36431387066841125}, {"Type": "FEAR", "Confidence": 0.09700098633766174}, {"Type": "DISGUSTED", "Confidence": 0.9556394815444946}, 
{"Type": "HAPPY", "Confidence": 41.95534133911133}, {"Type": "SAD", "Confidence": 0.3965829014778137}, {"Type": "ANGRY", "Confidence": 0.30273476243019104}, 
・・・（省略）・・・
```

## 3-4. デバイスからプログラムでWeb APIを利用する

[修正中]
Webアプリケーション内でステップ2-3を参考に....
