const auth = require('./utils/auth');
const config = require('./config/index');

App({
  globalData: {
    env: config.env,
    baseUrl: config.baseUrl,
    sessionID: '',
    userInfo: null
  },

  onLaunch() {
    this.globalData.sessionID = auth.getSessionID();
    this.globalData.userInfo = auth.getUserInfo();
  },

  setSession(sessionID) {
    this.globalData.sessionID = sessionID || '';
    auth.setSessionID(this.globalData.sessionID);
  },

  setUserInfo(userInfo) {
    this.globalData.userInfo = userInfo || null;
    auth.setUserInfo(this.globalData.userInfo);
  },

  isLoggedIn() {
    return auth.isLoggedIn();
  }
});
