import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '@/components/Home.vue'
import SearchFaces from '@/components/SearchFaces.vue'
import AnalysisFaces from '@/components/AnalysisFaces.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/search_faces',
    name: 'search_faces',
    component: SearchFaces
  },
  {
    path: '/analysis_faces',
    name: 'analysis_faces',
    component: AnalysisFaces
  },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
