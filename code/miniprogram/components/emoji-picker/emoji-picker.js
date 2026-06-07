Component({
  properties: {
    value: {
      type: String,
      value: ''
    }
  },

  data: {
    groups: [
      {
        name: '常用',
        emojis: ['😊', '🥴', '🤔', '😤', '😢', '😭', '😴', '🥳', '😎', '😍', '😨', '😰']
      },
      {
        name: '更多',
        emojis: ['😱', '😡', '🥺', '💀', '👻', '👽', '🤖', '👾', '😶', '🤐', '🥱', '😮']
      }
    ]
  },

  methods: {
    handleSelect(event) {
      const emoji = event.currentTarget.dataset.emoji;
      this.triggerEvent('change', { value: emoji });
    }
  }
});
