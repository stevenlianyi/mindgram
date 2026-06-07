const auth = require('../../../utils/auth');

Page({
  data: {
    userInfo: null,
    today: '',
    weekDay: '',
    streakDays: 5,
    previewList: [
      {
        postID: 'home-feed-1',
        moodEmoji: '😴',
        hintNote: '今天真的很累...',
        guessText: '3个好友猜对了'
      },
      {
        postID: 'home-feed-2',
        moodEmoji: '🥳',
        hintNote: '好消息值得庆祝!',
        guessText: '强度 8/10'
      }
    ],
    streakList: [true, true, true, true, true, false, false]
  },

  onShow() {
    const app = getApp();
    this.setData({
      userInfo: app.globalData.userInfo,
      today: this.formatToday(),
      weekDay: this.formatWeekDay(),
      streakDays: 5
    });
  },

  formatToday() {
    const now = new Date();
    const month = now.getMonth() + 1;
    const date = now.getDate();
    return `${month}月${date}日`;
  },

  formatWeekDay() {
    const names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    return names[new Date().getDay()];
  },

  goPost() {
    if (!auth.requireLogin()) return;
    wx.switchTab({
      url: '/pages/mood/post/post'
    });
  },

  goLogin() {
    wx.navigateTo({
      url: '/pages/auth/login/login'
    });
  }
});
