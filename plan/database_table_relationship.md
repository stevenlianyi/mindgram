# Mindgram 数据库表关系图

## 整体架构

```
                                  ┌─────────────────────┐
                                  │   mgSystemConfig    │  (独立系统配置表)
                                  │  PK: configID       │
                                  └─────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                    userBasic (用户体系核心)                                │
│                                    PK: loginID                                           │
└──────────────────────────────────────────────────────────────────────────────────────────┘
          │          │          │          │           │           │           │
          │ 1:N      │ 1:N      │ 1:N      │ 1:N       │ 1:N       │ 1:N       │ 1:N
          ▼          │          │          │           │           │           │
┌──────────────┐     │          │          │           │           │           │
│ mgUserStats  │     │          │          │           │           │           │
│ PK: userID   │     │          │          │           │           │           │
│ 积分/排名/打卡│     │          │          │           │           │           │
└──────────────┘     │          │          │           │           │           │
                     ▼          │          │           │           │           │
               ┌──────────┐     │          │           │           │           │
               │ mgFriend │ ←───┘ (userID / friendID 都指向 userBasic)
               │ PK: rela-│     │ 自引用：好友关系是用户到用户
               │  tionID  │     │           │           │           │
               │ 0请求中  │     │           │           │           │
               │ 1已接受  │     │           │           │           │
               │ 2已拒绝  │     │           │           │           │
               │ 3已拉黑  │     │           │           │           │
               └──────────┘     │           │           │           │
                                ▼           │           │           │
                          ┌───────────┐      │           │           │
                          │mgMoodPost │ ◄────┘           │           │
                          │PK: postID │   userID→作者     │           │
                          │Emoji/强度 │                  │           │
                          │提示语/匿名 │                  │           │
                          │照片/日期   │                  │           │
                          └───────────┘                  │           │
                           │         │                   │           │
                    1:N    │         │ 1:N               │           │
                           ▼         ▼                   │           │
                    ┌───────────┐ ┌──────────────┐       │           │
                    │mgMoodGuess│ │mgMoodReaction│       │           │
                    │PK:guessID │ │PK:reactionID │       │           │
                    │FK:postID──┼─│──FK:postID   │       │           │
                    │guesserID──┼─│──userID→回应用户│─────┘           │
                    │猜表情/积分 │ │heart/tears   │                   │
                    └───────────┘ │/laugh/hug    │                   │
                                  └──────────────┘                   │
                                      ┌──────────────────────────────┘
                                      ▼
                          ┌────────────────┐
                          │  mgInviteLink  │
                          │  PK: inviteID  │
                          │  userID→邀请人  │
                          │  邀请码/次数    │
                          └────────────────┘

┌──────────────────┐         ┌──────────────────┐
│   mgBadgeDef     │  1:N    │   mgUserBadge    │
│   PK: badgeID    │────────▶│   PK: recordID   │
│   徽章名称/图标   │  badgeID │   FK: userID ────▶ userBasic
│   条件类型/数值   │         │   FK: badgeID ───▶ mgBadgeDef
└──────────────────┘         │   获得时间/是否佩戴│
                             └──────────────────┘

              userBasic (loginID)
                   │
     ┌─────────────┼─────────────┬──────────────────┐
     │ 1:N         │ 1:N         │ 1:N              │ 1:N
     ▼             ▼             ▼                  ▼
┌──────────┐ ┌────────────┐ ┌──────────────┐ ┌──────────────┐
│mgWeekly  │ │mgAnnual    │ │mgQuarterly   │ │mgTcmDiagnosis│
│Reel      │ │Film        │ │Report        │ │              │
│PK:reelID │ │PK: filmID  │ │PK: reportID  │ │PK: tcmID     │
│周回顾视频 │ │年度电影     │ │季度情绪报告   │ │中医诊断       │
│主导Emoji  │ │四章场景     │ │表情分布/趋势  │ │五行/饮食/睡眠 │
└──────────┘ └────────────┘ └──────────────┘ └──────────────┘
```

---

## 14 张表清单

| # | 表名 | 主键 | 说明 |
|---|------|------|------|
| 1 | `userBasic` | loginID VARCHAR(32) | 用户基本信息 |
| 2 | `mgUserStats` | userID VARCHAR(32) | 用户积分/排名/打卡统计 |
| 3 | `mgFriend` | relationID BIGINT AUTO_INCREMENT | 好友关系 |
| 4 | `mgMoodPost` | postID BIGINT AUTO_INCREMENT | 打卡贴 |
| 5 | `mgMoodGuess` | guessID BIGINT AUTO_INCREMENT | 猜测记录 |
| 6 | `mgMoodReaction` | reactionID BIGINT AUTO_INCREMENT | 贴子回应 |
| 7 | `mgBadgeDef` | badgeID VARCHAR(16) | 徽章定义 |
| 8 | `mgUserBadge` | recordID BIGINT AUTO_INCREMENT | 用户徽章获得记录 |
| 9 | `mgWeeklyReel` | reelID BIGINT AUTO_INCREMENT | 周回顾视频 |
| 10 | `mgAnnualFilm` | filmID BIGINT AUTO_INCREMENT | 年度电影 |
| 11 | `mgQuarterlyReport` | reportID BIGINT AUTO_INCREMENT | 季度情绪报告 |
| 12 | `mgTcmDiagnosis` | tcmID BIGINT AUTO_INCREMENT | 中医诊断 |
| 13 | `mgInviteLink` | inviteID BIGINT AUTO_INCREMENT | 邀请链接 |
| 14 | `mgSystemConfig` | configID VARCHAR(32) | 系统配置（独立表） |

---

## 详细关联说明

### 用户体系（以 `userBasic` 为核心）

| 子表 | 关联字段 | 关系 | 说明 |
|------|----------|------|------|
| `mgUserStats` | userID → userBasic.loginID | **1:1** | 每个用户一条统计记录 |
| `mgFriend` | userID, friendID → userBasic.loginID | **N:N** (自引用) | 好友关系是用户到用户 |
| `mgMoodPost` | userID → userBasic.loginID | **1:N** | 一个用户有多条打卡帖 |
| `mgMoodGuess` | guesserID → userBasic.loginID | **1:N** | 一个用户可多次猜测 |
| `mgMoodReaction` | userID → userBasic.loginID | **1:N** | 一个用户可多次回应 |
| `mgInviteLink` | userID → userBasic.loginID | **1:N** | 一个用户可创建多条邀请 |
| `mgUserBadge` | userID → userBasic.loginID | **1:N** | 一个用户可获得多个徽章 |
| `mgWeeklyReel` | userID → userBasic.loginID | **1:N** | 一个用户有多期周回顾 |
| `mgAnnualFilm` | userID → userBasic.loginID | **1:N** | 一个用户有多部年度电影 |
| `mgQuarterlyReport` | userID → userBasic.loginID | **1:N** | 一个用户有多份季度报告 |
| `mgTcmDiagnosis` | userID → userBasic.loginID | **1:N** | 一个用户有多条中医诊断 |

### 帖子互动体系（以 `mgMoodPost` 为核心）

| 子表 | 关联字段 | 关系 | 说明 |
|------|----------|------|------|
| `mgMoodGuess` | postID → mgMoodPost.postID | **1:N** | 一个帖子有多条猜测 |
| `mgMoodReaction` | postID → mgMoodPost.postID | **1:N** | 一个帖子有多条回应 (heart/tears/laugh/hug) |

### 徽章体系

| 关系 | 说明 |
|------|------|
| `mgBadgeDef` → `mgUserBadge` | **1:N**，一个徽章可被多个用户获得 |

### 独立表

| 表 | 说明 |
|------|------|
| `mgSystemConfig` | 系统配置键值对，无外键关联 |

---

## 核心数据流

```
用户注册 → userBasic
    │
    ├─ 每日打卡 → mgMoodPost ─┬─ 好友猜测 → mgMoodGuess → 积分计入 mgUserStats
    │                         └─ 好友回应 → mgMoodReaction
    │
    ├─ 好友邀请 → mgInviteLink → mgFriend (建立关系)
    │
    ├─ 周回顾 → mgWeeklyReel (基于 mgMoodPost 聚合)
    ├─ 季度报告 → mgQuarterlyReport + mgTcmDiagnosis (AI分析)
    ├─ 年度电影 → mgAnnualFilm (年度总结)
    │
    └─ 成就系统 → mgBadgeDef → mgUserBadge (基于 mgUserStats 数据触发)
```
