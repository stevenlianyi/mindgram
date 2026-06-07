const { request } = require('../../../utils/request');
const auth = require('../../../utils/auth');

Page({
  data: {
    moodEmoji: '😊',
    hintNote: '',
    intensity: 5,
    isAnonymous: false,
    friendOnly: true,
    emotionTags: ['快乐', '疲惫', '焦虑'],
    selectedTag: '快乐',
    loading: false
  },

  onLoad() {
    auth.requireLogin();
  },

  handleEmojiChange(event) {
    this.setData({
      moodEmoji: event.detail.value
    });
  },

  handleHintInput(event) {
    this.setData({
      hintNote: event.detail.value
    });
  },

  handleIntensityChange(event) {
    this.setData({
      intensity: event.detail.value
    });
  },

  handleAnonymousChange(event) {
    this.setData({
      isAnonymous: event.detail.value
    });
  },

  handleFriendOnlyChange(event) {
    this.setData({
      friendOnly: event.detail.value
    });
  },

  handleTagSelect(event) {
    this.setData({
      selectedTag: event.currentTarget.dataset.tag
    });
  },

  async handleSubmit() {
    if (!this.data.moodEmoji) {
      wx.showToast({ title: '先选一个 Emoji', icon: 'none' });
      return;
    }

    if (this.data.loading) return;

    this.setData({ loading: true });

    try {
      const today = this.formatDate(new Date());
      const result = await request('mgmoodpostadd', {
        moodEmoji: this.data.moodEmoji,
        hintNote: this.data.hintNote,
        intensity: this.data.intensity,
        isAnonymous: this.data.isAnonymous ? '1' : '0',
        friendOnly: this.data.friendOnly ? '1' : '0',
        emotionTag: this.data.selectedTag,
        postDate: today
      });

      if (result.ok) {
        wx.showToast({
          title: '已发布',
          icon: 'success'
        });

        setTimeout(() => {
          wx.navigateTo({
            url: '/pages/feed/index/index'
          });
        }, 600);
      }
    } catch (err) {
      console.warn('post mood failed', err);
    } finally {
      this.setData({ loading: false });
    }
  },

  formatDate(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}${m}${d}`;
  }
});
