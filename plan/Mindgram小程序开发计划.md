# Mindgram 微信小程序开发计划

> 版本: v1.0 | 日期: 2026-06-06 | 目标平台: 微信小程序

---

## 一、项目概述

**Mindgram** 是一款面向大学生的情绪社交小程序，核心机制为「Emoji 打卡 + 自拍贴图 + 好友猜谜」，将情绪记录转化为社交互动游戏。计划覆盖 6 大核心功能模块（A001-A006）和 3 类配套支撑页面（C000-C002）。

---

## 二、技术架构

### 2.1 推荐技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| **小程序框架** | 微信原生 / Taro (React) | Taro 跨端能力强，原生性能最优 |
| **UI 组件库** | TDesign WeApp | 腾讯官方小程序组件库，设计规范统一 |
| **后端服务** | python + flask + Redis + MySQL 8.0 | 成熟稳定的服务端方案 |
| **缓存** | Redis 7.x | 排行榜、Session、热门数据缓存 |
| **文件存储** | 腾讯云 COS | 自拍照片、视频、GIF 存储 + CDN 加速 |
| **AI 服务** | Claude mindgramapi / 混元大模型 | 季度诊断报告、中医体质分析生成 |
| **视频生成** | FFmpeg + 腾讯云视频处理 | 周回顾短片、年度电影渲染 |
| **消息推送** | 微信订阅消息 | 打卡提醒、好友猜谜通知 |
| **监控** | 腾讯云可观测平台 | 接口监控、错误告警 |

### 2.2 备选方案：微信云开发

若团队规模小（1-2人），可考虑使用**微信云开发**（CloudBase）简化后端：

| 能力 | 替代方案 |
|------|---------|
| MySQL → 云开发数据库（NoSQL） | 需调整表结构为文档模型 |
| Redis → 云开发缓存 | 内置支持 |
| Python 服务 → 云函数 | 按量付费，免运维 |
| COS → 云存储 | 自带 CDN |

> 建议：MVP 阶段可用云开发快速验证，后期迁移到自建后端。

---

## 三、数据库设计（14 张表）

已有完整表结构定义，按业务域分组如下：

### 3.1 用户域
| 表名 | 文件 | 说明 |
|------|------|------|
| `userBasic` | userBasic.txt | 用户基础信息（含微信 openID） |
| `mgFriend` | mgFriend.txt | 好友关系（请求/接受/拉黑） |
| `mgInviteLink` | mgInviteLink.txt | 邀请码管理 |

### 3.2 核心社交域
| 表名 | 文件 | 说明 |
|------|------|------|
| `mgMoodPost` | mgMoodPost.txt | 情绪打卡贴（Emoji + 自拍 + 提示语） |
| `mgMoodGuess` | mgMoodGuess.txt | 好友猜测记录（猜对 +10 积分） |
| `mgMoodReaction` | mgMoodReaction.txt | 帖子回应（heart/tears/laugh/hug） |

### 3.3 激励域
| 表名 | 文件 | 说明 |
|------|------|------|
| `mgUserStats` | mgUserStats.txt | 用户统计（积分、连续打卡、排名） |
| `mgBadgeDef` | mgBadgeDef.txt | 徽章定义 |
| `mgUserBadge` | mgUserBadge.txt | 用户获得徽章记录 |

### 3.4 内容生成域
| 表名 | 文件 | 说明 |
|------|------|------|
| `mgWeeklyReel` | mgWeeklyReel.txt | 周情绪回顾短片 |
| `mgQuarterlyReport` | mgQuarterlyReport.txt | 季度诊断报告（AI 生成） |
| `mgAnnualFilm` | mgAnnualFilm.txt | 年度情绪电影 |
| `mgTcmDiagnosis` | mgTcmDiagnosis.txt | 中医体质诊断 |

### 3.5 系统域
| 表名 | 文件 | 说明 |
|------|------|------|
| `mgSystemConfig` | mgSystemConfig.txt | 系统配置项 |

### 3.6 统一审计字段规范

所有表均包含：`regID`, `regYMDHMS`, `modifyID`, `modifyYMDHMS`, `delFlag`（软删除标记）。

---

## 四、分阶段开发计划

### 🚀 Phase 0: 项目初始化（1 周）

**目标**：搭建开发环境、建立 CI/CD、完成基础架构。

| # | 任务 | 负责人 | 工时 |
|---|------|--------|------|
| 0.1 | 小程序项目创建（AppID 注册、目录结构） | 前端 | 0.5d |
| 0.2 | TDesign WeApp 组件库引入 + 主题定制 | 前端 | 0.5d |
| 0.3 | 后端项目初始化（Python Flask + MySQL + Redis 连接） | 后端 | 1d |
| 0.4 | 数据库建表（14 张表 DDL 编写与执行） | 后端 | 1d |
| 0.5 | 腾讯云 COS 存储桶创建 + SDK 集成 | 后端 | 0.5d |
| 0.6 | CI/CD 流水线搭建（代码仓库 + 自动部署） | DevOps | 1d |
| 0.7 | 统一错误码、日志、鉴权中间件 | 后端 | 1d |

**交付物**：
- 可运行的小程序骨架 + 后端服务
- 14 张数据库表就绪
- 基础鉴权流程（微信登录 → JWT Token）

---

### 🎯 Phase 1: MVP — 核心社交打卡（6-8 周）

**目标**：上线 A001 + A002 + C000，完成用户从注册到首次社交互动的闭环。

#### 1.1 用户系统 C000（2 周）

| # | 任务 | 涉及表 |
|---|------|--------|
| 1.1.1 | 微信一键登录（wx.login → openID → 自动注册） | userBasic |
| 1.1.2 | 个人资料编辑（昵称、头像、性别） | userBasic |
| 1.1.3 | 好友搜索（按昵称/ID） | userBasic |
| 1.1.4 | 好友申请/接受/拒绝/拉黑 | mgFriend |
| 1.1.5 | 邀请码生成与分享 | mgInviteLink |
| 1.1.6 | 好友列表 + 在线状态 | mgFriend |

**mindgramapi 接口清单**（6 个）：
```
POST   /mindgramapi/registration      微信登录
POST    /mindgramapi/getuserinfo             获取个人信息
POST    /mindgramapi/usermodify             修改个人信息
POST   /mindgramapi/friendrequest           发送好友申请
POST    /mindgramapi/friendrespond           处理好友申请
POST    /mindgramapi/friendlist              好友列表
POST   /mindgramapi/invitegenerate          生成邀请码
POST    /mindgramapi/invitevalidate          验证邀请码
```

#### 1.2 情绪打卡 A001（2.5 周）

| # | 任务 | 涉及表 |
|---|------|--------|
| 1.2.1 | Emoji 选择器组件（分类 + 搜索） | - |
| 1.2.2 | 谜语提示语输入（200 字限制） | - |
| 1.2.3 | 匿名模式开关 | - |
| 1.2.4 | 打卡发布（含日期校验，每日限 1 次） | mgMoodPost |
| 1.2.5 | 好友动态流（时间线 + 匿名标记） | mgMoodPost |
| 1.2.6 | 猜谜交互（选择 Emoji → 提交猜测 → 揭晓结果） | mgMoodGuess |
| 1.2.7 | 猜对动画 + 积分弹窗（+10 分） | mgUserStats |
| 1.2.8 | 帖子回应（heart/tears/laugh/hug 快捷反应） | mgMoodReaction |
| 1.2.9 | 7 天连续打卡追踪组件 | mgUserStats |
| 1.2.10 | 好友排行榜（周榜） | mgUserStats |

**mindgramapi 接口清单**（8 个）：
```
POST   /mindgramapi/moodpost                发布打卡
POST    /mindgramapi/moodtoday               获取今日打卡
POST    /mindgramapi/moodfeed                好友动态流（分页）
POST   /mindgramapi/moodguess               提交猜测
POST    /mindgramapi/moodguess-result    查看猜谜结果
POST   /mindgramapi/moodreaction            添加回应
POST    /mindgramapi/statsmine               我的统计
POST    /mindgramapi/statsleaderboard        排行榜
```

#### 1.3 自拍情绪贴图 A002（1.5 周）

| # | 任务 | 涉及表 |
|---|------|--------|
| 1.3.1 | 摄像头自拍组件（拍照 + 相册选择） | - |
| 1.3.2 | Emoji 贴图叠加（拖拽/缩放/旋转） | - |
| 1.3.3 | 情绪强度滑块（1-10 分） | - |
| 1.3.4 | 照片上传 COS + 缩略图生成 | mgMoodPost |
| 1.3.5 | 自拍预览与发布 | mgMoodPost |
| 1.3.6 | 动态流中自拍卡片展示 | mgMoodPost |

**mindgramapi 接口清单**（2 个）：
```
POST   /mindgramapi/uploadphoto             上传照片（返回 COS URL）
POST   /mindgramapi/moodpost-with-photo     发布带照片的打卡
```

#### 1.4 徽章系统（第 2 周并行）

| # | 任务 | 涉及表 |
|---|------|--------|
| 1.4.1 | 徽章数据初始化（共情达人/火热持续/匿名模式/自拍达人） | mgBadgeDef |
| 1.4.2 | 打卡时触发徽章检测（连续 7 天 → 火热持续） | mgUserBadge |
| 1.4.3 | 猜谜时触发徽章检测（累计猜对 10 次 → 共情达人） | mgUserBadge |
| 1.4.4 | 个人主页徽章墙展示 + 佩戴切换 | mgUserBadge |

**mindgramapi 接口清单**（3 个）：
```
POST    /mindgramapi/badgelist               徽章列表
POST   /mindgramapi/badgecheck             触发徽章检测（内部调用）
POST    /mindgramapi/badgewear          佩戴/取消佩戴徽章
```

**MVP 总计**：
- 小程序页面：约 12 个
- mindgramapi 接口：约 19 个
- 数据库表使用：9/14 张

---

### 📊 Phase 2: 周情绪回顾 A003（+4 周，累计 12 周）

**目标**：实现周回顾短片自动生成与分享。

| # | 任务 | 涉及表 |
|---|------|--------|
| 2.1 | 每周日晚自动触发视频生成（定时任务） | mgWeeklyReel |
| 2.2 | 视频模板设计（开场 Emoji 排列 → 每日滑动 → 主导情绪揭示） | mgWeeklyReel |
| 2.3 | FFmpeg 视频合成服务（图片 + 文字 + 转场动画） | - |
| 2.4 | GIF 导出（用于微信分享） | mgWeeklyReel |
| 2.5 | 周回顾预览页（视频播放 + 统计数据） | mgWeeklyReel |
| 2.6 | 分享页（统计数据卡片 + 主导情绪 + 社交分享） | mgWeeklyReel |
| 2.7 | 历史周回顾列表 | mgWeeklyReel |

**mindgramapi 接口清单**（4 个）：
```
POST    /mindgramapi/weeklycurrent           本周回顾
POST    /mindgramapi/weeklylist              历史回顾列表
POST    /mindgramapi/weeklyid               回顾详情
POST   /mindgramapi/weeklygenerate          手动生成回顾（测试用）
```

**新增表使用**：mgWeeklyReel（1 张）

**新增小程序页面**：约 4 个

---

### 📈 Phase 3: 季度诊断报告 A004（+2 周，累计 14 周）

**目标**：接入 AI 生成专业情绪诊断报告。

| # | 任务 | 涉及表 |
|---|------|--------|
| 3.1 | Claude/混元 API 集成层（Prompt 工程） | mgQuarterlyReport |
| 3.2 | 季度数据聚合（平均分/积极天数/连续打卡/Emoji 分布） | mgQuarterlyReport |
| 3.3 | 概览页（积极性/条形图/环形图/模式检测） | mgQuarterlyReport |
| 3.4 | 日度时间线（90 天彩色 Emoji 条带 + 13 周趋势） | mgQuarterlyReport |
| 3.5 | 诊断页（五项临床风格发现） | mgQuarterlyReport |
| 3.6 | 建议页（六张优先级行动卡片） | mgQuarterlyReport |
| 3.7 | 报告分享功能 | mgQuarterlyReport |

**mindgramapi 接口清单**（3 个）：
```
POST    /mindgramapi/reportquarterly   季度报告
POST    /mindgramapi/reportlist                 历史报告列表
POST   /mindgramapi/reportgenerate             触发生成报告
```

**新增表使用**：mgQuarterlyReport（1 张）

**新增小程序页面**：约 5 个（概览 + 时间线 + 诊断 + 建议 + 分享）

---

### 🌿 Phase 4: 中医养生建议 A005（+2 周，可与 Phase 3 并行）

**目标**：基于情绪数据映射中医体质诊断。

| # | 任务 | 涉及表 |
|---|------|--------|
| 4.1 | 中医诊断 AI Prompt 工程（五行映射模型） | mgTcmDiagnosis |
| 4.2 | 体质分析页（主证型 + 五行雷达图） | mgTcmDiagnosis |
| 4.3 | 饮食建议页（时辰表 + 八种食疗食材） | mgTcmDiagnosis |
| 4.4 | 睡眠建议页（四步晚间流程 + 穴位指导） | mgTcmDiagnosis |
| 4.5 | 身体时钟页（24 小时子午流注图交互） | mgTcmDiagnosis |
| 4.6 | 周养生计划页 | mgTcmDiagnosis |
| 4.7 | 免责声明组件（法律合规） | - |

**mindgramapi 接口清单**（2 个）：
```
POST    /mindgramapi/tcmdiagnosis     中医诊断结果
POST   /mindgramapi/tcmgenerate               触发生成诊断
```

**新增表使用**：mgTcmDiagnosis（1 张）

**新增小程序页面**：约 6 个

---

### 🎬 Phase 5: 年度情绪电影 A006（+4-6 周，累计 5-6 个月）

**目标**：生成 5 分钟电影级年度回顾视频。

| # | 任务 | 涉及表 |
|---|------|--------|
| 5.1 | 年度视频模板设计（四幕结构） | mgAnnualFilm |
| 5.2 | 开场动画（12 月迷你柱状图） | mgAnnualFilm |
| 5.3 | Q1 场景（热力图 + 网格动画） | mgAnnualFilm |
| 5.4 | Q2 场景（52 周曲线 + 峰值高亮） | mgAnnualFilm |
| 5.5 | Q3 场景（自拍肖像墙逐张淡入） | mgAnnualFilm |
| 5.6 | Q4 收尾（核心数据 + 韧性评分） | mgAnnualFilm |
| 5.7 | 章节目录 + 进度条拖拽播放器 | mgAnnualFilm |
| 5.8 | 旁白脚本生成（AI 文本 → TTS） | mgAnnualFilm |
| 5.9 | 视频导出与分享 | mgAnnualFilm |

**mindgramapi 接口清单**（3 个）：
```
POST    /mindgramapi/annualfilm             年度电影
POST    /mindgramapi/annuallist              历史列表
POST   /mindgramapi/annualgenerate          触发生成
```

**新增表使用**：mgAnnualFilm（1 张）

**新增小程序页面**：约 4 个

---

### 🔧 Phase 6: 补充与优化（持续）

| # | 任务 |
|---|------|
| 6.1 | C001 功能补充页面（关于/反馈/设置） |
| 6.2 | C002 动态流优化 + 截图分享（Canvas 绘制） |
| 6.3 | 性能优化（图片懒加载、分包加载、骨架屏） |
| 6.4 | 微信订阅消息推送（打卡提醒、好友猜谜通知） |
| 6.5 | 数据埋点与用户行为分析 |
| 6.6 | 冷启动策略（新用户引导、模拟好友体验） |
| 6.7 | 无障碍适配 |

---

## 五、小程序页面结构

```
pages/
├── auth/                          # 登录注册
│   ├── login/                     # 微信授权登录
│   └── profile-edit/              # 个人资料编辑
│
├── home/                          # 首页
│   ├── index/                     # 首页（今日情绪入口）
│   └── feed/                      # 好友动态流
│
├── mood/                          # A001 + A002 情绪打卡
│   ├── post/                      # 打卡发布页
│   ├── camera/                    # 自拍 + Emoji 贴图
│   └── detail/                    # 打卡详情 + 猜谜区域
│
├── social/                        # C000 社交
│   ├── friends/                   # 好友列表
│   ├── search/                    # 搜索用户
│   ├── invite/                    # 邀请好友
│   └── profile/                   # 他人主页
│
├── mine/                          # 个人中心
│   ├── index/                     # 我的主页
│   ├── badges/                    # 徽章墙
│   └── stats/                     # 统计数据
│
├── weekly/                        # A003 周回顾
│   ├── reel/                      # 周回顾视频播放
│   ├── history/                   # 历史回顾列表
│   └── share/                     # 分享页
│
├── report/                        # A004 季度报告
│   ├── overview/                  # 概览
│   ├── timeline/                  # 日度时间线
│   ├── diagnosis/                 # 诊断发现
│   └── advice/                    # 行动建议
│
├── tcm/                           # A005 中医养生
│   ├── constitution/              # 体质分析
│   ├── diet/                      # 饮食建议
│   ├── sleep/                     # 睡眠建议
│   ├── body-clock/                # 身体时钟
│   └── weekly-plan/               # 周养生计划
│
├── annual/                        # A006 年度电影
│   ├── film/                      # 电影播放
│   ├── chapters/                  # 章节目录
│   └── moments/                   # 自拍肖像墙
│
└── settings/                      # C001 设置
    ├── about/                     # 关于 Mindgram
    ├── feedback/                  # 意见反馈
    └── disclaimer/                # 免责声明
```

**总计约 30-35 个小程序页面**。

---

## 六、完整时间线与里程碑

```
Month 1          Month 2          Month 3          Month 4          Month 5          Month 6
|─────|─────|─────|─────|─────|─────|─────|─────|─────|─────|─────|─────|
| Init |                                                     
|      | MVP (A001+A002+C000)                                           |
|      |                    | A003 周回顾                                |
|      |                                         | A004 季度报告        |
|      |                                         | A005 中医养生 可并行 |
|      |                                                           | A006 |
|      |                                                           | 上线  |
```

| 里程碑 | 时间点 | 交付内容 |
|--------|--------|---------|
| **M0** 项目启动 | 第 1 周 | 架构搭建 + 数据库建表 |
| **M1** MVP 内测 | 第 8 周 | A001+A002+C000，可邀请种子用户 |
| **M2** 周回顾上线 | 第 12 周 | A003 视频生成 |
| **M3** 季度诊断上线 | 第 14 周 | A004 AI 报告 + A005 中医 |
| **M4** 年度电影上线 | 第 22 周 | A006 全功能完整版 |
| **M5** 公测发布 | 第 24 周 | 性能优化 + 正式上线 |

---

## 七、团队配置建议

| 角色 | 人数 | Phase 0-1 | Phase 2-3 | Phase 4-5 |
|------|------|-----------|-----------|-----------|
| **前端（小程序）** | 1-2 人 | 页面开发、组件库 | 视频播放器、图表 | 电影播放器、动画 |
| **后端（Python Flask）** | 1-2 人 | mindgramapi 开发、鉴权 | 定时任务、AI 集成 | 视频合成服务 |
| **AI/算法** | 0.5-1 人 | — | Prompt 工程 | 报告生成优化 |
| **UI/UX 设计** | 0.5 人 | 主界面设计 | 报告/视频设计 | 电影级视觉 |
| **测试** | 0.5 人 | 功能测试 | 回归测试 | 全量测试 |

**最小编制**：2 人全栈（前端 1 + 后端 1），可支撑到 Phase 3。AI 和设计可外包。

---

## 八、后端 mindgramapi 完整清单

> 所有接口统一使用 **POST** 方法，路径为扁平风格 `/mindgramapi/xxxx`。
> 请求参数通过 JSON Body 传递，认证通过 Header `Authorization: Bearer <JWT>` 传递。

### 8.1 认证模块（3 个）
```
POST   /mindgramapi/registration         微信登录（获取 openID，签发 JWT）
POST   /mindgramapi/authcheck            检查登录状态
POST   /mindgramapi/logout               退出登录
```

### 8.2 用户模块（3 个）
```
POST   /mindgramapi/getuserinfo          获取个人信息
POST   /mindgramapi/usermodify           修改个人信息
POST   /mindgramapi/usersearch           搜索用户（按昵称/ID）
```

### 8.3 好友模块（5 个）
```
POST   /mindgramapi/friendrequest        发送好友申请
POST   /mindgramapi/friendrespond        处理好友申请
POST   /mindgramapi/friendlist           好友列表
POST   /mindgramapi/friendpending        待处理申请列表
POST   /mindgramapi/frienddelete         删除好友
```

### 8.4 邀请模块（2 个）
```
POST   /mindgramapi/invitegenerate       生成邀请码
POST   /mindgramapi/invitevalidate       验证邀请码
```

### 8.5 情绪打卡模块（8 个）
```
POST   /mindgramapi/moodpost             发布打卡
POST   /mindgramapi/moodtoday            获取今日打卡
POST   /mindgramapi/mooddetail           打卡详情
POST   /mindgramapi/moodfeed             好友动态流（分页）
POST   /mindgramapi/moodcalendar         月度打卡日历
POST   /mindgramapi/moodguess            提交猜测
POST   /mindgramapi/moodguessresult      查看猜谜结果
POST   /mindgramapi/moodreaction         添加回应
```

### 8.6 上传模块（2 个）
```
POST   /mindgramapi/uploadphoto          上传照片
POST   /mindgramapi/uploadvideo          上传视频
```

### 8.7 统计模块（3 个）
```
POST   /mindgramapi/statsmine            我的统计
POST   /mindgramapi/statsleaderboard     排行榜（周/月）
POST   /mindgramapi/statsstreak          连续打卡信息
```

### 8.8 徽章模块（3 个）
```
POST   /mindgramapi/badgelist            所有徽章定义
POST   /mindgramapi/badgemine            我已获得徽章
POST   /mindgramapi/badgewear            佩戴/取消徽章
```

### 8.9 周回顾模块（4 个）
```
POST   /mindgramapi/weeklycurrent        本周回顾
POST   /mindgramapi/weeklylist           历史回顾列表
POST   /mindgramapi/weeklydetail         回顾详情
POST   /mindgramapi/weeklygenerate       触发生成
```

### 8.10 季度报告模块（3 个）
```
POST   /mindgramapi/reportquarterly      季度报告
POST   /mindgramapi/reportlist           历史报告列表
POST   /mindgramapi/reportgenerate       触发生成报告
```

### 8.11 中医养生模块（2 个）
```
POST   /mindgramapi/tcmdiagnosis         中医诊断
POST   /mindgramapi/tcmgenerate          触发生成诊断
```

### 8.12 年度电影模块（3 个）
```
POST   /mindgramapi/annualfilm          年度电影
POST   /mindgramapi/annuallist          历史列表
POST   /mindgramapi/annualgenerate      触发生成
```

### 8.13 系统模块（2 个）
```
POST   /mindgramapi/systemconfig        获取系统配置
POST   /mindgramapi/systemversion       获取版本信息
```

**总计 mindgramapi 接口：43 个**

---

## 九、关键风险与应对

| 风险 | 影响 | 概率 | 应对策略 |
|------|------|------|---------|
| **冷启动问题** | 高 | 高 | ① 强邀请机制（邀请码送积分）；② 单人模式有价值（日记 + 诊断）；③ 种子用户社群运营 |
| **AI 生成质量不稳定** | 中 | 中 | ① 多轮 Prompt 迭代优化；② 模板化 fallback 方案；③ 人工审核通道 |
| **视频生成耗时** | 中 | 中 | ① 异步任务队列（生成后推送通知）；② 预生成模板缓存；③ CDN 加速分发 |
| **微信审核不过** | 高 | 低 | ① 避免诱导分享文案；② 中医内容加免责声明；③ 用户发布内容审核 |
| **存储成本增长** | 中 | 高 | ① 照片压缩 + 缩略图；② 视频过期自动清理；③ COS 生命周期策略 |
| **性能瓶颈** | 中 | 中 | ① 分包加载；② 图片懒加载；③ Redis 热点缓存；④ 数据库索引优化 |

---

## 十、数据库索引建议

```sql
-- 高频查询索引
CREATE INDEX idx_moodpost_user_date  ON mgMoodPost(userID, postDate);
CREATE INDEX idx_moodpost_date       ON mgMoodPost(postDate);
CREATE INDEX idx_moodguess_post      ON mgMoodGuess(postID);
CREATE INDEX idx_moodguess_guesser   ON mgMoodGuess(guesserID);
CREATE INDEX idx_friend_user         ON mgFriend(userID);
CREATE INDEX idx_friend_friend       ON mgFriend(friendID);
CREATE INDEX idx_userstats_weekly    ON mgUserStats(weeklyScore DESC);
CREATE INDEX idx_userbadge_user      ON mgUserBadge(userID);

-- 去重约束
CREATE UNIQUE INDEX uk_moodpost_user_date ON mgMoodPost(userID, postDate) WHERE delFlag = '0';
CREATE UNIQUE INDEX uk_friend_pair       ON mgFriend(userID, friendID) WHERE delFlag = '0';
```

---

## 十一、环境与配置

| 环境 | 域名 | 用途 |
|------|------|------|
| **开发环境** | dev-mindgramapi.mindgram.cn | 日常开发联调 |
| **测试环境** | test-mindgramapi.mindgram.cn | QA 测试 |
| **预发布** | pre-mindgramapi.mindgram.cn | 上线前验证 |
| **生产环境** | mindgramapi.mindgram.cn | 正式服务 |

**小程序 AppID**：待申请
**COS Bucket**：`mindgram-{env}-125xxxxxxx`
**CDN 域名**：`cdn.mindgram.cn`

---

> **文档维护**：本文档随开发进度持续更新，重大变更需同步更新版本号和日期。

<｜｜DSML｜｜parameter name="explanation" string="true">生成 Mindgram 微信小程序开发计划文档