import Vue from 'vue';
import App from './App.vue';
import router from './router';
const API = 'http://localhost:3000/api/words';

Vue.config.productionTip = false;

const newApp = new Vue({
  el: '#app',
  router,
  data:{
		words:[],
		word:{
			id:'',
			name:'',
			gender:''
		}
	},
  render: h => h(App),
  created:function() {
		this.getWords();
	},
  methods:{
		getWords:function() {
			fetch(API)
			.then(res => () {
        res.json()
        console.log(res.json)
      })
			.then(res => this.words = res);
		},
	}
});
