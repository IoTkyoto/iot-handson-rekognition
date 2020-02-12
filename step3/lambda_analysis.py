# -*- coding: utf-8 -*-
"""
Rekognitionを利用して特定の画像に顔を分析するLambdaのためのコード
Method: POST
"""
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

# 定数
REKOGNITION_CLIENT = boto3.client('rekognition')
REQUIRED_KEYS: list = ['bucket_name', 'file_name']


class AnalyzeFaces():

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

          # Responseの作成
          payloads: dict = {}
          payloads['timestamp'] = self.make_timestamp()

          if 'FaceDetails' in data:
               payloads['analysis'] = data['FaceDetails']
               return self.make_response(200, '[SUCCEEDED]Analysis done', payloads)
          else:
               return self.make_response(404, '[FAILED]No face found')

     def analyze_faces(self, s3_bucket: str, s3_obj: str) -> dict:
          """
          画像の中から顔を検出し、その顔の分析結果を返す
          """
          try:
               analyze_result = REKOGNITION_CLIENT.detect_faces(
                    Image={
                         'S3Object': {
                         'Bucket': s3_bucket,
                         'Name': s3_obj
                         }
                    },
                    Attributes=["ALL"]
               )
               return self.create_response(analyze_result)
          
          # S3アクセス時のエラーに対処
          except Exception as error:
               return self.make_response(400, '[FAILED]{}'.format(error))


     def check_validation(self, body: dict):
          """
          バリデーションチェックをする関数
          """
          if not isinstance(body, dict):
               return self.make_response(400, '[FAILED]Invalid body type')
          
          errors: list = []
          for key in REQUIRED_KEYS:
               if not key in body.keys():
                    errors.append('key "{}" not found'.format(key))
               if body[key] == '':
                    errors.append('no value found for "{}"'.format(key))
               if not isinstance(body[key], str):
                    errors.append('invalid value type: "{}"'.format(body[key]))

          if errors:
               return self.make_response(400, '[FAILED]' + ', '.join(errors))
          else: 
               return


     def load_json(self, str_json: str) -> dict:
          """
          JSON文字列をPythonで処理できる形にする
          """
          if str_json is None:
               return self.make_response(400, '[FAILED]Data required')
          # Lambdaテスト時にdict型で入ってくるためif分岐
          if isinstance(str_json, str):
               # キー名がシングルクォーテーションで囲まれた場合jsonを変換できないためダブルクォーテーションに変換
               str_json = str_json.replace('\'', '"')
               return json.loads(str_json)
          else:
               return str_json


     def make_response(self, status_code: int, msg: str, payloads: dict = None):
               """
               レスポンスを作成する
               """
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

def lambda_handler(event, _):
     """
     /analyzeに対するPOSTをトリガーに実行
     """
     try:

          body = analyze_post.load_json(event['body'])
          if 'statusCode' in body:
               return body
          validation_errors = analyze_post.check_validation(body)
          if validation_errors:
               return validation_errors
          analyzing_result = analyze_post.analyze_faces(body['bucket_name'], body['file_name'])
          return analyzing_result
     except Exception as error:
          print('[DEBUG]: {}'.format(error))
          return analyze_post.make_response(500, '[FAILED]An error occurred : {}'.format(str(error)))