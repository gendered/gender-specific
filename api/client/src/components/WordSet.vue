<template>
  <div>
    <section :class="'word-set ' + word.gender">
      <span>{{ word.word }}</span>
      <span>{{ word.definition }}</span>
    </section>
    <!-- <section :class="'word-set ' + word.gender">
      <span>{{ word.word }}</span>
      <span>{{ word.definition }}</span>
    </section> -->
  </div>
</template>

<script>
  const API = 'http://localhost:3000/api/words/';

  export default {
    name: 'WordSet',
    props: ['id'],
    data() {
      return {
        word: {},
      }
    },
    created() {
      fetch(API + this.id)
      .then(res => res.json())
      .then(res => this.word = res);
    },
  };
</script>
