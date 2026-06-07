const config = require('../config/index');

function getSessionID() {
  return wx.getStorageSync(config.storageKeys.sessionID) || '';
}

function setSessionID(sessionID) {
  if (sessionID) {
    wx.setStorageSync(config.storageKeys.sessionID, sessionID);
  } else {
    wx.removeStorageSync(config.storageKeys.sessionID);
  }
}

function getUserInfo() {
  return wx.getStorageSync(config.storageKeys.userInfo) || null;
}

function setUserInfo(userInfo) {
  if (userInfo) {
    wx.setStorageSync(config.storageKeys.userInfo, userInfo);
  } else {
    wx.removeStorageSync(config.storageKeys.userInfo);
  }
}

function isLoggedIn() {
  return Boolean(getSessionID());
}

function clearLogin() {
  setSessionID('');
  setUserInfo(null);
}

function requireLogin() {
  if (!isLoggedIn()) {
    wx.navigateTo({
      url: '/pages/auth/login/login'
    });
    return false;
  }
  return true;
}

module.exports = {
  getSessionID,
  setSessionID,
  getUserInfo,
  setUserInfo,
  isLoggedIn,
  clearLogin,
  requireLogin
};
