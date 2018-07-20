import WordList from '@/components/WordList'
import FilterPanel from '@/components/FilterPanel'
const API = 'http://localhost:3000/api/words';

export default {
  name: 'Home',
  components: {
    WordList,
    FilterPanel
  },
  data() {
    return {
      activeFilters: [],
      tags: [
        {
          'name': 'tag',
          'type': 'urban',
        },
        {
          'name': 'tag',
          'type': 'wordnik',
        },
        {
          'name': 'tag',
          'type': 'webster',
        },
        {
          'name': 'tag',
          'type': 'datamuse',
        },
      ],
      sex: [
        {
          'name': 'sex',
          'type': 'female'
        },
        {
          'name': 'sex',
          'type': 'male'
        }
      ],
      words: [],
    }
  },
  created() {
    fetch(API)
    .then(res => res.json())
    .then((res) => {
      this.words = this.sort(res)
    });
  },
  computed: {
    filtered () {
      var filtered = this.words;
      this.activeFilters.forEach(filter => {
        filtered = filtered.filter(entry => {
          switch (filter.name) {
            case 'sex':
              return entry['gender'] === filter.type;
              break
            case 'tag':
              if (entry['tags']) {
                console.log(entry['tags'], filter.type)
                return entry['tags'].includes(filter.type);
              }
              break;
          }
        });
      });
      return filtered;
    }
  },
  methods: {
    sort(arr) {
      return arr.sort(function(a, b){
        if (a.word < b.word) return -1;
        if (a.word > b.word) return 1;
        return 0;
      });
    },
    handleFilter(option) {
      let activeFilters = this.activeFilters;
      let index = -1;
      const name = option.name;
      const type = option.type;
      let obj = {
        'name': name,
        'type': type
      };
      // if it's not you can add or remove
      if (activeFilters) {
        index = this.activeFilters.findIndex(i => i.name === option.name);
        if (index === -1) {
          this.addFilter(obj);
        }
        else {
          this.removeFilter(index);
        }
      }
      else {
        this.addFilter(obj);
      }
    },
    addFilter(option) {
      this.activeFilters.push(option);
    },
    removeFilter(idx) {
      this.activeFilters.splice(idx, 1);
    }
  }
}
