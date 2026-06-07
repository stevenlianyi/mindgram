const { request } = require('../../../utils/request');
const config = require('../../../config/index');

Page({
  data: {
    loading: false
  },

  handleLogin() {
    if (this.data.loading) return;

    this.setData({ loading: true });

    if (config.mockAuth) {
      const app = getApp();

      app.setSession(config.mockSessionID);
      app.setUserInfo(config.mockUser);

      setTimeout(() => {
        this.setData({ loading: false });
        wx.switchTab({
          url: '/pages/home/index/index'
        });
      }, 500);
      return;
    }

    wx.login({
      success: async (loginRes) => {
        try {
          const result = await request('registration', {
            code: loginRes.code,
            clientType: 'miniProgram',
            lang: 'CN'
          });

          if (result.ok) {
            const data = result.data || {};
            const app = getApp();
            const sessionID = data.sessionID || data.rawSessionID || result.raw.sessionID || '';
            const userInfo = {
              loginID: data.loginID || result.raw.loginID || '',
              nickName: data.nickName || 'Mindgram 用户',
              avatarID: data.avatarID || ''
            };

            app.setSession(sessionID);
            app.setUserInfo(userInfo);

            wx.switchTab({
              url: '/pages/home/index/index'
            });
          }
        } catch (err) {
          console.warn('login failed', err);
        } finally {
          this.setData({ loading: false });
        }
      },
      fail: () => {
        this.setData({ loading: false });
        wx.showToast({
          title: '无法获取微信登录凭证',
          icon: 'none'
        });
      }
    });
  }
});
