# -*- coding: utf-8 -*-
"""
Rekognitionのコレクションにアクセスし、登録されている顔かどうか認証するLambdaのためのコード
Method: POST
"""
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
import base64
import uuid
import botocore.exceptions

REKOGNITION_CLIENT = boto3.client('rekognition')
# Rekognitionで作成したコレクション名を入れてください
COLLECTION_ID = 'yamada-authentication-collection'
# Rekognitionで一度に検出したい顔の最大数（最大4096人まで可）
MAX_FACES = 10

class Rekognition():
     def __init__(self):
          self.required_keys: list
          self.optional_keys: list
          self.rekognition_client = REKOGNITION_CLIENT
          self.collection_id = COLLECTION_ID
          self.max_faces = MAX_FACES

     # def convert_to_float(self, data) -> float:
     #      """
     #      受け取ったオブジェクトをFloat型にする
     #      """
     #      return float(data)
     
     # def round_to_2nd_decimal(self, data) -> float:
     #      """
     #      受け取った数値を小数点第三位で四捨五入する
     #      """
     #      return round(data, 2)

     def make_timestamp(self) -> str: 
          """
          タイムスタンプを作成する
          """
          date_now = datetime.now()
          return str(date_now.strftime('%Y-%m-%d %H:%M:%S'))

     def create_response(self, data: dict):
          """
          Rekognition結果を解析し、Response Bodyのデータを作成する
          """
          print('[DEBUG]create_response()')
          payloads: dict = {}
          payloads['timestamp'] = self.make_timestamp()
          payloads.update(data)
          return self.make_response(200, '[SUCCEEDED]Rekognition done', payloads)

     def decode_base64_to_binary(self, image_base64: str) -> bytes:
          """
          base64のデータをバイナリデータに変換する
          """
          print('[DEBUG]decode_base64_to_binary()')
          return base64.b64decode(image_base64)

     def search_face(self, image_binary: bytes, threshold: float = None) -> dict:
          """
          画像とマッチする人物を特定する
          """
          print('[DEBUG]search_face()')
          try:
               search_result = REKOGNITION_CLIENT.search_faces_by_image(
                    CollectionId=self.collection_id,
                    Image={
                         'Bytes': image_binary
                    },
                    MaxFaces=self.max_faces,
                    FaceMatchThreshold=threshold
               )
               return self.create_response(search_result)

          # # 画像内に顔を認識出来ない場合
          # except botocore.exceptions.InvalidParameterException as error:
          #      print('[DEBUG]: {}'.format(error))
          #      return self.make_response(421, '画像内に人物の顔を認識出来ませんでした')
          
          # # 画像サイズが制限オーバーの場合
          # except botocore.exceptions.ImageTooLargeException as error:
          #      print('[DEBUG]: {}'.format(error))
          #      return self.make_response(422, '画像のサイズが大きすぎます（制限:15MB）')
          
          # # 画像フォーマットが異なる場合
          # except botocore.exceptions.InvalidImageFormatException as error:
          #      print('[DEBUG]: {}'.format(error))
          #      return self.make_response(423, '画像のフォーマットが異なります（制限:PNGあるいはJPEG形式）')
          
          # その他エラーに対処
          except Exception as error:
               print('[DEBUG]: {}'.format(error))
               error_code = error.response['Error']['Code']
               if (error_code == 'InvalidParameterException'):
                    return self.make_response(421, '画像内に人物の顔を認識出来ませんでした')
               elif (error_code == 'ImageTooLargeException'):
                    return self.make_response(422, '画像のサイズが大きすぎます（制限:15MB）')
               elif (error_code == 'InvalidImageFormatException'):
                    return self.make_response(423, '画像のフォーマットが異なります（制限:PNGあるいはJPEG形式）')
               else:
                    return self.make_response(500, '[FAILED]{}'.format(error))
               
     def check_validation(self, body: dict):
          """
          バリデーションチェックをする関数
          """
          print('[DEBUG]check_validation()')
          if not body:
               return self.make_response(400, '[FAILED]Data required')
          if not isinstance(body, dict):
               return self.make_response(400, '[FAILED]Invalid body type')
          
          errors: list = []
          for key_info in self.required_keys:
               key_name: str = key_info['name']
               key_type: tuple = key_info['type']
               if not key_name in body.keys():
                    errors.append('key "{}" not found'.format(key_name))
               elif body[key_name] == '':
                    errors.append('no value found for "{}"'.format(key_name))
               elif not isinstance(body[key_name], key_type):
                    errors.append('invalid value type: "{}"'.format(key_name))
          for key_info in self.optional_keys:
               key_name = key_info['name']
               key_type = key_info['type']
               if key_name in body.keys():
                    if not isinstance(body[key_name], key_type):
                         errors.append('invalid value type: "{}"'.format(key_name))
                    elif bool not in key_type and isinstance(body[key_name], bool):
                         errors.append('invalid value type: "{}"'.format(key_name))
          if errors:
               return self.make_response(400, '[FAILED]' + ', '.join(errors))
          else: 
               return

     def load_json(self, str_json: str) -> dict:
          """
          JSON文字列をPythonで処理できる形にする
          """
          print('[DEBUG]load_json()')
          if str_json is None:
               return self.make_response(400, '[FAILED]Data required')
          # Lambdaテスト時にdict型で入ってくるためif分岐
          if isinstance(str_json, str):
               try:
                    return json.loads(str_json)
               except json.JSONDecodeError:
                    print('[DEBUG]json decode error')
                    return self.make_response(400, '[FAILED]json decode error')
          else:
               return str_json

     def make_response(self, status_code: int, msg: str, payloads: dict = None):
          """
          レスポンスを作成する
          """
          print('[DEBUG]make_response()')
          if payloads:
               body = json.dumps({'msg': msg, 'payloads': payloads})
          else:
               body = json.dumps({'msg': msg})
          print(body)
          return {
               'statusCode': status_code,
               'headers': {
                    "Access-Control-Allow-Origin" : "*",
               },
               'body': body,
          }

     def search_post(self, event):
          """
          （メイン処理）データをチェックし、問題がない場合はRekognitionにかける
          """
          self.required_keys = [{'name': 'image_base64', 'type': (str)}]
          self.optional_keys = [{'name': 'threshold', 'type': (float, int)}]
          
          body = self.load_json(event['body'])
          if 'statusCode' in body:
               return body
          validation_errors = self.check_validation(body)
          if validation_errors:
               return validation_errors
          image_binary = self.decode_base64_to_binary(body['image_base64'])
          # 画像認識実施
          search_result = self.search_face(image_binary, body['threshold'])
          return search_result

#　初期化
rekognition = Rekognition()

def lambda_handler(event, _):
     """
     /searchに対するPOSTをトリガーに、最初に実行される関数
     """
     try:
          response_data = rekognition.search_post(event)
          print('[DEBUG]response data: {}'.format(response_data))
          return response_data
     except Exception as error:
          print('[DEBUG]500:{}'.format(error))
          return rekognition.make_response(500, '[FAILED]An error occurred : {}'.format(str(error)))
