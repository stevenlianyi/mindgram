const { request } = require('../../../utils/request');

Page({
  data: {
    loading: false,
    friends: [],
    leaderboard: [
      { rank: '🥇', name: '小红', score: 280 },
      { rank: '🥈', name: '小明', score: 245 },
      { rank: '🥉', name: '小刚', score: 190 },
      { rank: '4', name: '小美', score: 165 }
    ]
  },

  onShow() {
    this.loadFriends();
  },

  async loadFriends() {
    if (this.data.loading) return;
    this.setData({ loading: true });

    try {
      const result = await request('mgfriendqry', {
        beginNum: 0,
        endNum: 49
      }, { toast: false });

      this.setData({
        friends: this.extractList(result)
      });
    } catch (err) {
      this.setData({ friends: [] });
      console.warn('load friends failed', err);
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

  handleInvite() {
    wx.showShareMenu({
      withShareTicket: true
    });

    wx.showToast({
      title: '可通过右上角分享',
      icon: 'none'
    });
  },

  onShareAppMessage() {
    return {
      title: '来 Mindgram 猜猜我的心情',
      path: '/pages/home/index/index'
    };
  }
});
