const auth = require('../../../utils/auth');

Page({
  data: {
    userInfo: null,
    isLoggedIn: false
  },

  onShow() {
    const app = getApp();
    this.setData({
      userInfo: app.globalData.userInfo,
      isLoggedIn: auth.isLoggedIn()
    });
  },

  goLogin() {
    wx.navigateTo({
      url: '/pages/auth/login/login'
    });
  },

  handleLogout() {
    const app = getApp();
    auth.clearLogin();
    app.globalData.sessionID = '';
    app.globalData.userInfo = null;
    this.setData({
      userInfo: null,
      isLoggedIn: false
    });
  }
});
