# -*- coding: utf-8 -*-
"""
Rekognitionを利用して特定の画像に顔を分析するLambdaのためのコード
Method: POST
"""
import json
import boto3
from typing import Union, Tuple
from datetime import datetime
import botocore.exceptions
import base64

# 定数
REKOGNITION_CLIENT = boto3.client('rekognition')
REQUIRED_KEYS: list = [{'name': 'image_base64str', 'type': (str,)}]

class AnalyzeFaces():
     def __init__(self):
          self.rekognition_client = REKOGNITION_CLIENT
          self.required_keys = REQUIRED_KEYS
     

     def make_timestamp(self) -> str: 
          """
          タイムスタンプを作成する
          """
          date_now = datetime.now()
          return str(date_now.strftime('%Y-%m-%d %H:%M:%S'))

     def create_response(self, data: dict) -> dict:
          """
          Rekognition結果を解析し、Response Bodyのデータを作成する
          """
          print('[DEBUG]create_response()')
          payloads: dict = {}
          payloads['timestamp'] = self.make_timestamp()

          if 'FaceDetails' in data:
               payloads['analysis'] = data['FaceDetails']
               return self.make_response(200, '[SUCCEEDED]Analysis done', payloads)
          else:
               return self.make_response(404, '[FAILED]No face found')

     def decode_base64_to_binary(self, image_base64str: str) -> bytes:
          """
          base64のデータをバイナリデータに変換する
          """
          print('[DEBUG]decode_base64_to_binary()')
          # 画像データから不要な値を抜き出す(コンマがない場合は不要な値がないとし、全文字列を利用)
          image_base64str = image_base64str[image_base64str.find(',') + 1 :]
          return base64.b64decode(image_base64str)
          
     def analyze_faces(self, image_binary: bytes) -> dict:
          """
          画像の中から顔を検出し、その顔の分析結果を返す
          """
          print('[DEBUG]analyze_faces()')
          try:
               analysis_result = self.rekognition_client.detect_faces(
                    Image={
                         'Bytes': image_binary
                    },
                    Attributes=["ALL"]
               )
               return self.create_response(analysis_result)
          
          # S3アクセス時のエラーに対処
          except Exception as error:
               print('[DEBUG]: {}'.format(error))
               return self.make_response(400, '[FAILED]{}'.format(error))
               # error_code = error.response['Error']['Code']
               # if (error_code == 'InvalidParameterException'):
               #      return self.make_response(421, '画像内に人物の顔を認識出来ませんでした')
               # elif (error_code == 'ImageTooLargeException'):
               #      return self.make_response(422, '画像のサイズが大きすぎます（制限:15MB）')
               # elif (error_code == 'InvalidImageFormatException'):
               #      return self.make_response(423, '画像のフォーマットが異なります（制限:PNGあるいはJPEG形式）')
               # else:
               #      return self.make_response(500, '[FAILED]{}'.format(error))

     def check_validation(self, body: dict) -> Union[None, dict]:
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
               elif type(body[key_name]) not in key_type:
                    errors.append('invalid value type: "{}"'.format(key_name))

          if errors:
               return self.make_response(400, '[FAILED]' + ', '.join(errors))
          else: 
               return None

     def load_json(self, str_json: str) -> Tuple[bool, dict]:
          """
          JSON文字列をPythonで処理できる形にする
          """
          print('[DEBUG]load_json()')
          if str_json is None:
               return False, self.make_response(400, '[FAILED]Data required')
          # Lambdaテスト時にdict型で入ってくるためif分岐
          if isinstance(str_json, str):
               try:
                    return True, json.loads(str_json)
               except json.JSONDecodeError:
                    print('[DEBUG]json decode error')
                    return False, self.make_response(400, '[FAILED]json decode error')
          else:
               return True, str_json

     def make_response(self, status_code: int, msg: str, payloads: dict = None) -> dict:
               """
               レスポンスを作成する
               """
               print('[DEBUG]make_response()')
               if payloads:
                    body = json.dumps({'msg': msg, 'payloads': payloads})
               else:
                    body = json.dumps({'msg': msg})

               return {
                    'statusCode': status_code,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': body,
               }


#　初期化
analyze_post = AnalyzeFaces()

def lambda_handler(event, _) -> dict:
     """
     /analyzeに対するPOSTをトリガーに実行
     """
     try:
          # リクエストボディの中の文字列型JSONデータをPythonで扱える形に変換する
          result, body = analyze_post.load_json(event['body'])
          if not result:
               return body
          # リクエストボディの中に必要なパラメータがあるかや型が合っているかをチェックする
          validation_errors = analyze_post.check_validation(body)
          if validation_errors:
               return validation_errors
          # リクエストボディから送られた画像データをバイナリに変換しRekognitionが受け取れる形にする
          image_binary = analyze_post.decode_base64_to_binary(body['image_base64str'])
          # 画像認識を行い、結果を返す
          analyzing_result = analyze_post.analyze_faces(image_binary)
          return analyzing_result
     except Exception as error:
          print('[DEBUG]500: {}'.format(error))
          return analyze_post.make_response(500, '[FAILED]An error occurred : {}'.format(str(error)))
