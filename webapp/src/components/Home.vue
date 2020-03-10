<template>
  <v-row align="start" justify="center">
    <v-col cols="12">
      <v-card color="#385F73" dark>
        <v-card-title class="headline">人物認識</v-card-title>
        <v-card-subtitle>ステップ２：顔認証のWeb APIを作成する</v-card-subtitle>
        <v-card-text>
          <div>スマートフォンで撮影した写真に誰が写っているかを認識させましょう</div>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
            <v-btn text @click="gotoSearchFacesPage()">
              <v-icon dark>mdi-account-question</v-icon>
              人物認識画面へ
            </v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
    <v-col cols="12">
      <v-card color="#385F73" dark>
        <v-card-title class="headline">顔画像分析</v-card-title>
        <v-card-subtitle>
          ステップ３：顔画像分析結果を取得するWeb APIを作成する<br>
          ステップ４：ログデータをクラウドにアップロードする
        </v-card-subtitle>
        <v-card-text>
          <div>スマートフォンで撮影した写真の人物の分析を行わせましょう</div>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="gotoAnalysisfacesPage()">
            <v-icon dark>mdi-face-recognition</v-icon>
            顔画像分析画面へ
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
  export default {
    name: 'Home',
    data: () => ({
    }),
    methods: {
      gotoSearchFacesPage() {
        this.$router.push('/search_faces');
      },
      gotoAnalysisfacesPage() {
        this.$router.push('/analysis_faces');
      },
    }
  };
</script>>