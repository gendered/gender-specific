<template>
  <input type="submit" @click="clicked :value="text" />
</template>

<script>
export default {
  name: 'Button',
  props: ['text'],
  methods: {
    clicked() {
    }
  },
};
</script>
