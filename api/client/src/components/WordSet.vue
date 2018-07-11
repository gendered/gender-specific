<template>
  <div>
    <section :class="'word-set ' + data.gender">
      <span>{{ data.word }}</span>
      <span>{{ data.definition }}</span>
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
    props: ['word'],
    data() {
      return {
        data: {},
      }
    },
    created() {
      const w = this.word;
      let obj = { "where": { "word": w } };
      const url = `${API}findOne?filter${obj}`
      fetch(url)
      .then(res => res.json())
      .then((res) => {
        console.log(res);
      });
    },
  };
</script>
