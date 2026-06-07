const config = require('../config/index');
const auth = require('./auth');

function normalizeResult(raw) {
  const result = raw || {};
  const errCode = result.errCode || result.code || '';
  const ok = !errCode || errCode === 'B0' || errCode === '0' || errCode === 0;

  return {
    ok,
    errCode,
    message: getMessage(result),
    data: result.data || result.DATA || result,
    raw: result
  };
}

function getMessage(result) {
  if (!result) return '';
  if (typeof result.MSG === 'string') return result.MSG;
  if (result.MSG && result.MSG.content) return result.MSG.content;
  if (result.message) return result.message;
  if (result.errMsg) return result.errMsg;
  return '';
}

function request(urlPath, data = {}, options = {}) {
  const sessionID = auth.getSessionID();
  const cleanPath = String(urlPath || '').replace(/^\/+/, '');
  const payload = Object.assign({}, data);

  if (sessionID && !payload.sessionID) {
    payload.sessionID = sessionID;
  }

  if (config.mockApi) {
    return Promise.resolve(mockRequest(cleanPath, payload));
  }

  return new Promise((resolve, reject) => {
    wx.request({
      url: `${config.baseUrl}${config.apiPrefix}/${cleanPath}`,
      method: options.method || 'POST',
      data: payload,
      timeout: options.timeout || config.requestTimeout || 3000,
      header: Object.assign({
        'content-type': 'application/json'
      }, options.header || {}),
      success(res) {
        const normalized = normalizeResult(res.data);

        if (!normalized.ok && options.toast !== false) {
          wx.showToast({
            title: normalized.message || '请求失败',
            icon: 'none'
          });
        }

        resolve(normalized);
      },
      fail(err) {
        const fallback = getFallbackResult(cleanPath, payload);

        if (fallback && options.fallback !== false) {
          console.warn(`request fallback: ${cleanPath}`, err);
          resolve(fallback);
          return;
        }

        if (options.toast !== false) {
          wx.showToast({
            title: '网络不可用',
            icon: 'none'
          });
        }
        reject(err);
      }
    });
  });
}

function getFallbackResult(urlPath, data) {
  if (!config.enableApiFallback) return null;
  return mockRequest(urlPath, data);
}

function mockRequest(urlPath, data) {
  const mockData = {
    registration: {
      sessionID: config.mockSessionID,
      loginID: config.mockUser.loginID,
      nickName: config.mockUser.nickName,
      avatarID: config.mockUser.avatarID
    },
    mgmoodpostqry: {
      total: 2,
      data: [
        {
          postID: 'mock-post-001',
          userID: 'friend_001',
          nickName: '林间同学',
          moodEmoji: '🥲',
          intensity: 6,
          hintNote: '不是难过，只是今天有点想安静。',
          isAnonymous: '0',
          postDate: '2小时前',
          heartCount: 12,
          tearCount: 3,
          laughCount: 5,
          hugCount: 8
        },
        {
          postID: 'mock-post-002',
          userID: 'friend_002',
          nickName: '匿名朋友',
          moodEmoji: '✨',
          intensity: 8,
          hintNote: '猜猜是什么事让我突然充满电。',
          isAnonymous: '1',
          postDate: '1小时前',
          heartCount: 8,
          tearCount: 1,
          laughCount: 2,
          hugCount: 6
        }
      ]
    },
    mgfriendqry: {
      total: 2,
      data: [
        {
          relationID: 'mock-friend-001',
          friendID: 'friend_001',
          nickName: '林间同学',
          status: '已添加',
          todayMood: '😊 快乐',
          streak: '🔥12天'
        },
        {
          relationID: 'mock-friend-002',
          friendID: 'friend_002',
          nickName: '晚自习搭子',
          status: '已添加',
          todayMood: '😴 疲惫',
          streak: '🔥5天'
        }
      ]
    },
    mgmoodpostadd: {
      postID: `mock-post-${Date.now()}`,
      saved: true,
      payload: data
    }
  };

  return normalizeResult({
    errCode: 'B0',
    data: mockData[urlPath] || {}
  });
}

module.exports = {
  request,
  normalizeResult
};
