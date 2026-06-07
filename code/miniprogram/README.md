# Mindgram Mini Program

Mindgram 小程序前端使用微信原生 WXML/WXSS/JS 开发。当前 UI 按 `plan/UI` 原型以原生组件实现，暂不依赖 TDesign，以避开微信开发者工具 npm 组件编译问题。

## 首次打开项目

1. 在当前目录安装依赖：

   ```bash
   npm install
   ```

2. 用微信开发者工具打开 `code/miniprogram`。

3. 当前页面不依赖 npm 组件，可以直接编译。若后续重新启用 TDesign，再在微信开发者工具中执行：

   ```text
   工具 -> 构建 npm
   ```

4. 构建完成后，应生成本地目录：

   ```text
   code/miniprogram/miniprogram_npm/tdesign-miniprogram/
   ```

当前 `app.json` 不再引用 `tdesign-miniprogram/*` 组件，项目配置也会忽略 `node_modules/` 和 `miniprogram_npm/`，因此不执行“构建 npm”也应能编译。

如果微信开发者工具出现 `getDevCodeByFileList` 相关内部编译错误，优先检查项目详情里的编译设置：

- 关闭“过滤无依赖文件”
- 关闭“增强编译”
- 关闭“热重载”
- 重新点击“编译”

## 本地配置

后端接口地址在 `config/index.js` 中维护，默认开发环境为：

```js
baseUrl: 'http://127.0.0.1:5000'
```

## 无 AppID 开发模式

当前项目默认开启无 AppID 开发模式：

```js
mockAuth: true
mockApi: true
enableApiFallback: true
```

开启后，登录页不会调用 `wx.login`，而是写入本地 mock session 和 mock 用户；动态、好友、发布接口也会返回本地示例数据，避免后端未启动时出现请求超时。

`enableApiFallback` 会在真实接口请求失败时回落到本地示例数据，适合已经设置 AppID 但后端服务还没启动的阶段。

拿到真实小程序 AppID 后：

1. 将 `project.config.json` 中的 `appid` 从 `touristappid` 改为真实 AppID。
2. 将 `config/index.js` 中的 `mockAuth`、`mockApi` 和 `enableApiFallback` 改为 `false`。
3. 重新编译并验证 `wx.login -> /mindgramapi/registration` 登录链路。

`node_modules/` 和 `miniprogram_npm/` 都是本地依赖或构建产物，不提交到 Git。
