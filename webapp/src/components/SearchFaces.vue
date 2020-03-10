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
          <v-toolbar-title>人物認識</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-dialog v-model="settingDialogRecognition" persistent max-width="600px">
            <template v-slot:activator="{ on }">
              <v-btn icon dark v-on="on">
                <v-icon>mdi-account-question</v-icon>
              </v-btn>
            </template>
            <v-card>
              <v-card-title>
                <span class="headline">人物認識設定</span>
              </v-card-title>
              <v-card-text>
                <v-container>
                  <v-text-field v-model="apiId" label="API ID名" clearable></v-text-field>
                  <v-text-field v-model="region" label="リージョン" clearable></v-text-field>
                  <v-text-field v-model="stage" label="ステージ名" clearable></v-text-field>
                  <v-text-field v-model="resource" label="リソース名" clearable></v-text-field>
                  <v-text-field v-model="apiKey" label="APIキー" clearable></v-text-field>
                  <v-select
                    v-model="threshold"
                    :items="[10,20,30,40,50,60,70,80,90,100]"
                    label="しきい値"
                    clearable>
                  </v-select>
                </v-container>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="warning" @click="settingDialogRecognition = false" block large><v-icon left>mdi-content-save</v-icon>保存</v-btn>
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-toolbar>
        <v-card-text>
          <v-form>
            <v-file-input show-size label="画像ファイルを選択" accept="image/*" @change="onFileChange"></v-file-input>
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
            <div v-show="faceMatch">
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th>マッチした人物</th>
                      <th>信頼度</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>{{faceMatch}}</td>
                      <td>{{faceMatchConf}}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </div>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
            <v-btn color="warning" class="ma-2 white--text" x-large @click="execRecognition" v-if="uploadedImage">
              <v-icon dark>mdi-cloud-upload</v-icon>
              &nbsp;人物認識実行
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

  export default {
    name: 'SearchFaces',

    data: () => ({
      uploadedImage: '',
      noTarget: false,
      overlay: false,
      successMessage: '',
      errorMessage: '',
      settingDialogRecognition: false,
      faceMatch: false,
      faceMatchConf: null,
    }),
    created() {
      this.apiId = this.config.searchConfig.apiId;
      this.region = this.config.searchConfig.region;
      this.stage = this.config.searchConfig.stage;
      this.resource = this.config.searchConfig.resource;
      this.apiKey = this.config.searchConfig.apiKey
      this.threshold = this.config.searchConfig.threshold
    },
    methods: {
      /**
       * 画像変更時処理
       */
      onFileChange(e) {
        this.noTarget = false;
        if (e != null) {
          this.createImage(e);
          this.uploadedImage = false;
          this.faceMatch = false;
        } else {
          this.uploadedImage = false;
          this.faceMatch = false;
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
       * 顔認識実行処理
       */
      execRecognition() {
        // 設定情報入力チェック
        this.errorMessage = ''
        if (!this.apiId) {
          this.errorMessage = "設定画面でAPI ID名を入力してください";
        } else if (!this.region) {
          this.errorMessage = "設定画面でAPIのリージョンを入力してください";
        } else if (!this.stage) {
          this.errorMessage = "設定画面でAPIのステージ名を入力してください";
        } else if (!this.resource) {
          this.errorMessage = "設定画面でAPIのリソース名を入力してください";
        } else if (!this.apiKey) {
          this.errorMessage = "設定画面でAPIキーを入力してください";
        }else if (!this.threshold) {
          this.errorMessage = "設定画面でしきい値を入力してください";
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
          'threshold': this.threshold,
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
              const faceMatches = response.data.payloads.FaceMatches;
              if (faceMatches.length == 0) {
                this.noTarget = '人物を特定できませんでした'
              } else {
                this.createAuthenticationData(faceMatches[0]);
              }
              this.overlay = false;
          })
          .catch(error => {
            this.errorMessage = error;
            this.overlay = false;
          });
      },
      /**
       * 顔認識結果編集処理
       */
      createAuthenticationData(faceMatch) {
        this.faceMatch = faceMatch.Face.ExternalImageId;
        this.faceMatchConf = Math.round(faceMatch.Similarity * 100) / 100 + '%';
      }
    }
  };
</script>>