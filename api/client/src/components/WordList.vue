<template>
  <div class="word-list">
    <ul v-if="words && words.length">
       <li v-for="word of words">
         <a :href="'./words/' + word.word">{{word.word}}</a>
       </li>
     </ul>
  </div>
</template>

<script>
  const API = 'http://localhost:3000/api/words';
  export default {
    name: 'WordList',
    props: ['words'],
  };
</script>
