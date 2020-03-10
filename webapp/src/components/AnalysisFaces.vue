<template>
  <v-row align="start" justify="center">
    <v-col cols="12" sm="8" md="6">
      <v-alert type="error" v-if="errorMessage">
        {{errorMessage}}
      </v-alert>
      <v-alert type="success" v-if="successMessage">
        {{successMessage}}
      </v-alert>
      <v-card class="elevation-12">
        <v-toolbar color="indigo lighten-3" dark flat>
          <v-toolbar-title>顔画像分析</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-dialog v-model="settingDialogRecognition" persistent max-width="600px">
            <template v-slot:activator="{ on }">
              <v-btn icon dark v-on="on">
                <v-icon>mdi-face-recognition</v-icon>
              </v-btn>
            </template>
            <v-card>
              <v-card-title>
                <span class="headline">顔画像分析設定</span>
              </v-card-title>
              <v-card-text>
                <v-container>
                  <v-text-field v-model="apiId" label="API ID名" clearable></v-text-field>
                  <v-text-field v-model="region" label="リージョン" clearable></v-text-field>
                  <v-text-field v-model="stage" label="ステージ名" clearable></v-text-field>
                  <v-text-field v-model="resource" label="リソース名" clearable></v-text-field>
                  <v-text-field v-model="apiKey" label="APIキー" clearable></v-text-field>
                </v-container>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="warning" @click="settingDialogRecognition = false" block large><v-icon left>mdi-content-save</v-icon>保存</v-btn>
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-dialog>
          <v-dialog v-model="settingDialogPublish" persistent max-width="600px">
            <template v-slot:activator="{ on }">
              <v-btn icon dark v-on="on">
                <v-icon>mdi-file-upload</v-icon>
              </v-btn>
            </template>
            <v-card>
              <v-card-title>
                <span class="headline"> Publish設定</span>
              </v-card-title>
              <v-card-text>
                <v-container>
                  <v-text-field v-model="accessKeyID" label="アクセスキーID" clearable required></v-text-field>
                  <v-text-field v-model="secretAccessKey" label="シークレットアクセスキー" clearable required></v-text-field>
                  <v-select
                    v-model="region"
                    :items="['ap-northeast-1','ap-northeast-2','ap-northeast-3', 
                      'us-east-1','us-east-2','us-west-1','us-west-2','ap-southeast-1','ap-southeast-2' ]"
                    label="リージョン"
                    clearable>
                  </v-select>
                  <v-text-field v-model="iotCoreID" label="AWS IoT エンドポイントID" clearable></v-text-field>
                  <v-text-field v-model="topicName" label="トピック名" clearable></v-text-field>
                </v-container>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="warning" @click="publishSettingSave" block large><v-icon left>mdi-content-save</v-icon>保存</v-btn>
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-toolbar>
        <v-card-text>
          <v-form>
            <v-chip
              class="ma-2"
              color="warning"
              v-if="publishSettingComplete"
            >
              Publish設定完了
            </v-chip>
            <v-file-input show-size label="File input" accept="image/*" @change="onFileChange"></v-file-input>
            <div class="preview-item" style="text-align: center;">
              <img
                v-show="uploadedImage"
                class="preview-item-file"
                :src="uploadedImage"
                alt=""
                width="200px"
              />
            </div>
            <div v-show="noTarget"><v-text-field label="認識結果" v-model='noTarget' outlined editable></v-text-field></div>
            <div v-show="analysisGender">
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th class="text-left">項目</th>
                      <th class="text-left">値</th>
                      <th class="text-left">信頼度</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>年齢</td>
                      <td>{{analysisAgeMin}} 〜 {{analysisAgeMax}} 歳</td>
                      <td>{{analysisAgeConf}}</td>
                    </tr>
                    <tr>
                      <td>性別</td>
                      <td>{{analysisGender}}</td>
                      <td>{{analysisGenderConf}}</td>
                    </tr>
                    <tr>
                      <td>笑顔</td>
                      <td>{{analysisSmile}}</td>
                      <td>{{analysisSmileConf}}</td>
                    </tr>
                    <tr>
                      <td>メガネ</td>
                      <td>{{analysisEyeglasses}}</td>
                      <td>{{analysisEyeglassesConf}}</td>
                    </tr>
                    <tr>
                      <td>口ひげ</td>
                      <td>{{analysisMustache}}</td>
                      <td>{{analysisMustacheConf}}</td>
                    </tr>
                    <tr>
                      <td>あごひげ</td>
                      <td>{{analysisBeard}}</td>
                      <td>{{analysisBeardConf}}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </div>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
            <v-btn color="warning" class="ma-2 white--text" x-large @click="execAnalysis" v-if="uploadedImage">
              <v-icon dark>mdi-face-recognition</v-icon>
              &nbsp;顔画像分析実行
            </v-btn>
          <v-spacer />
        </v-card-actions>
      </v-card>
      <v-overlay :value="overlay">
        <v-progress-circular indeterminate size="64"></v-progress-circular>
      </v-overlay>
    </v-col>
  </v-row>
</template>

<script>
  import axios from 'axios';
  import AWS from 'aws-sdk';
  import moment from "moment";

  export default {
    name: 'AnalysisFaces',

    data: () => ({
      file: null,
      uploadedImage: '',
      noTarget: '',
      overlay: false,
      info: '',
      successMessage: '',
      errorMessage: '',
      settingDialogRecognition: false,
      settingDialogPublish: false,
      publishSettingComplete: false,
      analysisAgeMin: null,
      analysisAgeMax: null,
      analysisAgeConf: `-`,
      analysisGender: false,
      analysisGenderConf: null,
      analysisSmile: true,
      analysisSmileConf: null,
      analysisEyeglasses: true,
      analysisEyeglassesConf: null,
      analysisMustache: true,
      analysisMustacheConf: null,
      analysisBeard: true,
      analysisBeardConf: null,
    }),
    created() {
      this.apiId = this.config.analysisConfig.apiId;
      this.region = this.config.analysisConfig.region;
      this.stage = this.config.analysisConfig.stage;
      this.resource = this.config.analysisConfig.resource;
      this.apiKey = this.config.analysisConfig.apiKey;
      this.accessKeyID = this.config.uploadConfig.accessKeyID;
      this.secretAccessKey = this.config.uploadConfig.secretAccessKey;
      this.iotCoreID = this.config.uploadConfig.iotCoreID;
      this.topicName = this.config.uploadConfig.topicName;
      this.checkPublishSettingComplete();
    },
    methods: {
      /**
       * 画像変更時処理
       */
      onFileChange(e) {
        this.noTarget = '';
        if (e != null) {
          this.createImage(e);
          this.uploadedImage = false;
          this.analysisGender = false;
        } else {
          this.uploadedImage = false;
          this.analysisGender = false;
        }
        this.errorMessage = '';
      },
      /**
       * 画像取得処理
       */
      createImage(file) {
        const reader = new FileReader();
        reader.onload = e => {
          this.uploadedImage = e.target.result;
        };
        reader.readAsDataURL(file);
      },
      /**
       * アップロード設定保存処理
       */
      publishSettingSave() {
        this.settingDialogPublish = false;
        this.checkPublishSettingComplete();
      },
      /**
       * アップロード設定完了チェック
       */
      checkPublishSettingComplete() {
        if (!this.accessKeyID || !this.secretAccessKey || !this.region || !this.iotCoreID || !this.topicName) {
          this.publishSettingComplete = false;
        } else {
          this.publishSettingComplete = true;
        }
      },
      /**
       * 画像分析実施処理メソッド
       */
      execAnalysis() {
        // 設定情報入力チェック
        if (this.apiId == '') {
          this.errorMessage = "設定画面でAPI ID名を入力してください";
        } else if (this.region == '') {
          this.errorMessage = "設定画面でAPIのリージョンを入力してください";
        } else if (this.stage == '') {
          this.errorMessage = "設定画面でAPIのステージ名を入力してください";
        } else if (this.resource == '') {
          this.errorMessage = "設定画面でAPIのリソース名を入力してください";
        } else if (this.apiKey == '') {
          this.errorMessage = "設定画面でAPIキーを入力してください";
        }
        // エラー時は処理終了
        if (this.errorMessage) {
          return
        } else {
          this.overlay = true;
        }
        // 実行時パラメータ構築
        const querydata = {
          'image_base64str': this.uploadedImage,
        };
        const config = {headers: {
          'Content-Type': 'application/json',
          'x-api-key': this.apiKey,
        }};
        const apiEndpoint = 
          'https://' + this.apiId + '.execute-api.' + this.region + '.amazonaws.com/'  
          + this.stage + '/' + this.resource
        // API呼び出し
        axios
          .post(apiEndpoint, JSON.stringify(querydata), config)
          .then(response => {
              const analysisData = response.data.payloads.analysis;
              if (analysisData.length == 0) {
                this.noTarget = '顔が認識できません';
              } else {
                this.createAnalysisData(analysisData["0"]);
                this.execPublish(analysisData["0"]);
              }
              this.overlay = false;
          })
          .catch(error => {
            this.errorMessage = error;
            this.overlay = false;
          });
      },
      /**
       * 小数点以下２桁編集処理
       */
      roundToTwoDecimalPlaces(num) {
        return Math.round(num * 100) / 100;
      },
      /**
       * 分析結果編集処理
       */
      createAnalysisData(analysisData) {
        var displayGender = 'その他';
        if (analysisData.Gender.Value == 'Male') {
          displayGender = `男性`;
        } else if (analysisData.Gender.Value == 'Female') {
          displayGender = `女性`;
        }
        this.analysisAgeMin = analysisData.AgeRange.Low;
        this.analysisAgeMax = analysisData.AgeRange.High;
        this.analysisGender = displayGender;
        this.analysisGenderConf = this.roundToTwoDecimalPlaces(analysisData.Gender.Confidence) + '%';
        this.analysisSmile = analysisData.Smile.Value ? 'はい' : 'いいえ';
        this.analysisSmileConf = this.roundToTwoDecimalPlaces(analysisData.Smile.Confidence) + '%';
        this.analysisEyeglasses = analysisData.Eyeglasses.Value ? 'はい' : 'いいえ';
        this.analysisEyeglassesConf = this.roundToTwoDecimalPlaces(analysisData.Eyeglasses.Confidence) + '%';
        this.analysisMustache = analysisData.Mustache.Value ? 'はい' : 'いいえ';
        this.analysisMustacheConf = this.roundToTwoDecimalPlaces(analysisData.Mustache.Confidence) + '%';
        this.analysisBeard = analysisData.Beard.Value ? 'はい' : 'いいえ';
        this.analysisBeardConf = this.roundToTwoDecimalPlaces(analysisData.Beard.Confidence) + '%';
      },
      /**
       * 顔分析結果データのpublish処理メソッド
       * Publish設定が完了していない場合は何も処理しない
       */
      execPublish(analysisData) {
        if (this.publishSettingComplete) {
          // SDKで使用するAWS認証情報の更新
          AWS.config.update({
            credentials: new AWS.Credentials(
              this.accessKeyID,
              this.secretAccessKey
            ),
            region: this.region
          });
          // IoTエンドポイントの構築
          const iotEndpoint = this.iotCoreID + '.iot.' + this.region + '.amazonaws.com';
          // IoTDataクラスのインスタンス化
          const iotdata = new AWS.IotData({
            endpoint: iotEndpoint,
            apiVersion: '2015-05-28'
          });
          // 送信データの作成
          const datetime = moment(new Date()).format("YYYY-MM-DD HH:mm:ss")
          const payload = {
            "Datetime": datetime,
            "AgeRange-Low": analysisData.AgeRange.Low,
            "AgeRange-High": analysisData.AgeRange.High,
            "Gender": analysisData.Gender.Value,
            "Smile": analysisData.Smile.Value,
            "Eyeglasses": analysisData.Eyeglasses.Value,
            "Sunglasses": analysisData.Sunglasses.Value,
            "Beard": analysisData.Beard.Value,
            "Mustache": analysisData.Mustache.Value,
            "EyesOpen": analysisData.EyesOpen.Value,
            "MouthOpen": analysisData.MouthOpen.Value
          }
          // パラメータの設定
          var params = {
            topic: this.topicName,
            payload: JSON.stringify(payload),
            qos: '0'
          };
          // Publish実行
          iotdata.publish(params, function(err, data) {
            if (err) console.log(err, err.stack);
            else     console.log(data);
          });
        } else {
          console.log('設定未完了のためPublish処理は行わない');
        }
      }
    }
  };
</script>>