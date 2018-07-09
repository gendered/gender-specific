<template>
  <div class="home">
    <ul v-if="words && words.length">
       <li v-for="word of words">
         <span>{{word.word}}</span>
       </li>
     </ul>
  </div>
</template>

<script>
const API = 'http://localhost:3000/api/words';

export default {
  name: 'home',
  data() {
    return {
      words: [],
    }
  },
  created() {
    fetch(API)
    .then(res => res.json())
    .then(res => this.words = res);
  },
};
</script>
<style lang="scss">
  ul {
    display: flex;
    flex-wrap: wrap;
    height: 100%;
    list-style: none;

    li {
      padding: 15px;
    }
  }
</style>
