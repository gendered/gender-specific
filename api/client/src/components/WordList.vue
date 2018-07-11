<template>
  <div class="word-list">
    <ul v-if="words && words.length">
       <li v-for="word of words">
         <a href="">{{word.word}}</a>
       </li>
     </ul>
  </div>
</template>

<script>
export default {
  name: 'WordList',
  props: ['words'],
};
</script>
