const { request } = require('../../../utils/request');

Page({
  data: {
    loading: false,
    moodList: []
  },

  onShow() {
    this.loadFeed();
  },

  async loadFeed() {
    if (this.data.loading) return;
    this.setData({ loading: true });

    try {
      const result = await request('mgmoodpostqry', {
        beginNum: 0,
        endNum: 19
      }, { toast: false });

      const list = this.extractList(result);
      this.setData({ moodList: list });
    } catch (err) {
      this.setData({ moodList: [] });
      console.warn('load feed failed', err);
    } finally {
      this.setData({ loading: false });
    }
  },

  extractList(result) {
    const data = result.data || {};
    if (Array.isArray(data)) return data;
    if (Array.isArray(data.data)) return data.data;
    if (Array.isArray(result.raw && result.raw.data)) return result.raw.data;
    return [];
  },

  goPost() {
    wx.switchTab({
      url: '/pages/mood/post/post'
    });
  },

  handleGuess(event) {
    wx.showToast({
      title: `准备猜 ${event.detail.postID || ''}`,
      icon: 'none'
    });
  }
});
