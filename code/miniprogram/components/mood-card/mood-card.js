Component({
  properties: {
    item: {
      type: Object,
      value: {}
    }
  },

  methods: {
    handleGuess() {
      this.triggerEvent('guess', {
        postID: this.data.item.postID
      });
    }
  }
});
