<template>
  <div class="filter-options">
    <ul v-if="options && options.length">
       <li v-for="option in options">
          <input type="submit" :value="option" />
       </li>
     </ul>
  </div>
</template>

<script>
export default {
  name: 'FilterPanel',
  props: ['options'],
};
</script>
