<template>
  <div class="home">
     <WordList></WordList>
     <FilterPanel :options="tags"></FilterPanel>
     <FilterPanel :options="sex"></FilterPanel>
  </div>
</template>

<script>
  import WordList from '@/components/WordList'
  import FilterPanel from '@/components/FilterPanel'

  export default {
    name: 'Home',
    components: {
      WordList,
      FilterPanel
    },
    data() {
      return {
        tags: ['urban', 'webster', 'wordnik'],
        sex: ['female', 'male'],
      }
    },
  }
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
