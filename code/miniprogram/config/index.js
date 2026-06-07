const env = 'dev';

const envConfig = {
  dev: {
    baseUrl: 'http://127.0.0.1:5000'
  },
  test: {
    baseUrl: 'https://test-mindgramapi.mindgram.cn'
  },
  prod: {
    baseUrl: 'https://mindgramapi.mindgram.cn'
  }
};

module.exports = {
  env,
  baseUrl: envConfig[env].baseUrl,
  apiPrefix: '/mindgramapi',
  requestTimeout: 3000,
  mockAuth: true,
  mockApi: true,
  enableApiFallback: true,
  mockSessionID: 'mock-session-dev',
  mockUser: {
    loginID: 'mock_user_001',
    nickName: 'Mindgram 开发用户',
    avatarID: ''
  },
  storageKeys: {
    sessionID: 'mindgram_session_id',
    userInfo: 'mindgram_user_info'
  }
};
