import Vue from 'vue'
import App from './views/app/App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import config from './mixins/ConfigMixin'

Vue.mixin(config)
Vue.config.productionTip = false

new Vue({
  router,
  vuetify,
  render: h => h(App)
}).$mount('#app')
