# 贴吧自动签到 · Tieba Auto Sign-in

每天自动给百度贴吧中你**关注的所有吧**签到。每次运行都会重新拉取关注列表，**新关注的吧自动纳入**，无需手动维护名单。

基于 [aiotieba](https://github.com/Starry-OvO/aiotieba)（贴吧官方 App 接口的 Python 实现，长期维护），无任何第三方服务依赖。

## 功能

- ✅ 自动签到所有已关注的贴吧
- ✅ 本地运行，或 GitHub Actions 云端定时（关机也能签）
- ✅ 新关注的吧自动加入
- ✅ 个别吧失败（如被吧务封禁）逐个列出，不影响其他吧

## 快速开始

### 1. 获取 BDUSS（一次性的）

1. 浏览器登录 [tieba.baidu.com](https://tieba.baidu.com)
2. 按 `F12` → **Application** → **Cookies** → `https://tieba.baidu.com` → 复制 `BDUSS` 的值
3. 这是你的登录凭证，**不要泄露给任何人**

### 2. 方式一：本地运行

```bash
pip install -r requirements.txt
python sign.py "你的BDUSS"
```

BDUSS 三种提供方式（任选其一）：

| 方式 | 做法 |
|---|---|
| 命令行参数 | `python sign.py "你的BDUSS"` |
| 环境变量 | 设置 `TIEBA_BDUSS` 后运行 `python sign.py` |
| 本地文件 | 与 `sign.py` 同目录新建 `bduss.txt`，内容为 BDUSS |

### 3. 方式二：GitHub Actions 云端定时（推荐，关机也能签）

1. **Fork** 本仓库
2. 仓库 **Settings → Secrets and variables → Actions** → New repository secret：Name 填 `TIEBA_BDUSS`，Value 填你的 BDUSS
3. 进入 **Actions** 标签启用 workflow
4. 默认每天 **00:30（北京时间）** 自动签到；也可手动 **Run workflow** 立刻签一次

## 输出示例

```
正在登录并拉取关注贴吧列表……
  [OK]   某某吧  (Lv.7)
  [FAIL] 被封的吧 : (3250004, '您的帐号涉及违规操作，现已被吧务团队封禁，可进行申诉。')
------------------------------------------------
关注吧总数: 35 | 新签到成功: 23 | 今日已签: 11 | 失败: 1
```

## 安全提醒

`BDUSS` 等于你百度账号的登录态（相当于密码）。请只放在自己的设备或私有 Secrets 里，**绝不要提交到公开仓库**——`.gitignore` 已排除 `bduss.txt`。

## License

[MIT](LICENSE)
