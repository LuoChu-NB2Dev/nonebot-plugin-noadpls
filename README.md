<!-- markdownlint-disable MD031 MD033 MD036 MD041 -->

<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# nonebot-plugin-noadpls

_✨ 群聊发广告 哒咩~ ✨_

<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
<a href="https://docs.astral.sh/uv">
  <img src="https://img.shields.io/badge/uv-managed-blueviolet" alt="uv-managed">
</a>
<a href="https://wakatime.com/badge/github/LuoChu-NB2Dev/nonebot-plugin-noadpls">
  <img src="https://wakatime.com/badge/github/LuoChu-NB2Dev/nonebot-plugin-noadpls.svg" alt="wakatime">
</a>

<br />

<!-- <a href="https://pydantic.dev">
  <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v1.json" alt="Pydantic Version 1" >
</a> -->
<!-- <a href="https://pydantic.dev">
  <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json" alt="Pydantic Version 2" >
</a> -->
<a href="https://pydantic.dev">
  <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/pyd-v1-or-v2.json" alt="Pydantic Version 1 Or 2" >
</a>
<a href="./LICENSE">
  <img src="https://img.shields.io/github/license/LuoChu-NB2Dev/nonebot-plugin-noadpls.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-noadpls">
  <img src="https://img.shields.io/pypi/v/nonebot-plugin-noadpls.svg" alt="pypi">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-noadpls">
  <img src="https://img.shields.io/pypi/dm/nonebot-plugin-noadpls" alt="pypi download">
</a>

<br />

<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-noadpls:nonebot_plugin_noadpls">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin%2Fnonebot-plugin-noadpls" alt="NoneBot Registry">
</a>
<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-noadpls:nonebot_plugin_noadpls">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin-adapters%2Fnonebot-plugin-noadpls" alt="Supported Adapters">
</a>

</div>

## 📖 介绍

这是一个用于屏蔽群聊中广告的插件，诞生于一个朋友的需求。

通用匹配所有群聊消息，提取文本并对图片OCR，与预定义词库和用户定义词库进行模糊匹配。
会自动撤回并禁言，禁言时间可配置。
如你是管理员或群主，可以私聊bot订阅禁言通知，以防误禁言和扯皮。

> [!TIP]
> 主要针对 QQ 群聊环境进行开发和测试，其他平台不保证可用。

DONE:

- [x] 对图片进行 OCR 识别
- [x] 对文本进行模糊匹配
- [x] 排除字符对识别影响，如"代.理"
- [x] 支持自定义屏蔽词
- [x] 支持管理员/群主私聊订阅禁言通知
- [x] 支持自定义禁言时间
- [x] 支持分群可选是否启用插件(仅data)

TODO:

- [ ] 支持自定义屏蔽词文件路径
- [ ] 支持拆分字，近形字，拼音判断
- [ ] 支持分群可选是否禁言，撤回，仅通知管理
- [ ] 支持二维码识别
- [ ] 用户自定义屏蔽词文件路径读取
- [ ] 管理员/群主私聊调整插件配置

## 💿 安装

以下提到的方法 任选**其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot-plugin-noadpls
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-noadpls
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-plugin-noadpls
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-noadpls
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-noadpls
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_noadpls"
]
```

</details>

## ⚙️ 配置

在 nonebot2 项目的 `.env` 文件中的可选配置

|         配置项         |   类型    |     默认值      |          说明          |
| :--------------------: | :-------: | :-------------: | :--------------------: |
|    noadpls__enable     |   Bool    |      True       |      是否启用插件      |
|   noadpls__priority    |    Int    |       10        |       插件优先级       |
| *noadpls__ban_pre_text | List[str] | ["advertisement"] | 启用的预定义屏蔽词词库 |

- *详细内容请参见 [TelechaBot/cleanse-speech](https://github.com/TelechaBot/cleanse-speech/blob/main/src/cleanse_speech/bookshelf.py)
  TL;DR 太长不看版
  - `advertisement`：默认中文广告词库
  - `pornographic`：默认中文色情词库
  - `politics`: 默认中文敏感词库
  - `general`: 默认中文通用词库
  - `netease`: 网易屏蔽词库

插件同时使用 [nonebot-plugin-localstore](https://github.com/nonebot/plugin-localstore/) 插件存储 `可变配置`,`插件数据`和`缓存文件`，具体配置方法请参见 [nonebot-plugin-localstore 存储路径](https://github.com/nonebot/plugin-localstore/blob/master/README.md#%E5%AD%98%E5%82%A8%E8%B7%AF%E5%BE%84) 和 [nonebot-plugin-localstore 配置项](https://github.com/nonebot/plugin-localstore/blob/master/README.md#%E9%85%8D%E7%BD%AE%E9%A1%B9)

将会存储在 `localstore` 定义的配置存储文件中的配置项

|    配置项     |   类型    |            默认值            |                说明                |
| :-----------: | :-------: | :--------------------------: | :--------------------------------: |
|   ban_time    | List[int] | [60, 300, 1800, 3600, 86400] |            禁言时间列表            |
|   ban_text    | List[str] |             [ ]              |          用户自定义屏蔽词          |
| ban_text_path | List[str] |             [ ]              | 用户自定义屏蔽词文件路径(还没写好) |

> [!WARNING]
> 不推荐用户自行更改可变配置文件
> ~~推荐使用私聊指令进行更新~~ 指令更新还没写好()

## 🎉 使用

### 指令表

|      指令      |   权限   | 需要@ | 范围  |       说明       |
| :------------: | :------: | :---: | :---: | :--------------: |
|                |  所有人  |  否   | 群聊  | 通用匹配所有消息 |
| *接收通知 群号 | 管理以上 |  否   | 私聊  | 开启接收禁言通知 |
| *关闭通知 群号 | 管理以上 |  否   | 私聊  | 取消接收禁言通知 |
| *nap_on **群号 | 管理以上 |  否   | 私聊  | 开启群检测 |
| *nap_off **群号 | 管理以上 |  否   | 私聊  | 关闭群检测 |

- *非管理以上权限也可私聊，但是会提示无权限
- **当在群聊环境中使用时，`群号`会自动填充为当前群号

### 效果图

![开启通知](./resources/开启通知.png "开启通知")
![群成员群聊触发处理](./resources/群成员群聊触发处理.png "群成员群聊触发处理")
![群成员触发私聊通知-抹除qq号](./resources/群成员触发私聊通知-抹除qq号.png "群成员触发私聊通知-抹除qq号")
![管理员群聊触发处理](./resources/管理员群聊触发处理.png "管理员群聊触发处理")
![管理员触发私聊通知-抹除qq号](./resources/管理员触发私聊通知-抹除qq号.png "管理员触发私聊通知-抹除qq号")

## 📊 统计

![Alt](https://repobeats.axiom.co/api/embed/10188b8616c4e05811e91f43fb73051d1b188991.svg "Repobeats analytics image")

## 📞 联系

QQ：3214528055  
Discord：[@洛初](https://discordapp.com/users/959299637049700355)  
Telegram：[@Furinature](https://t.me/Furinature)  
吹水群：[611124274](https://qm.qq.com/q/BS2k2XIfxS)  
邮箱：<gongfuture@outlook.com>

## 💡 鸣谢

感谢帮忙测试的各位群友~

感谢以下项目：

- [nonebot-plugin-localstore](https://github.com/nonebot/plugin-localstore) 提供了本地文件存储支持
- [TelechaBot/cleanse-speech](https://github.com/TelechaBot/cleanse-speech) 使用了基础屏蔽机制和预定义词库
- [nonebot_paddle_ocr](https://github.com/canxin121/nonebot_paddle_ocr) 参考了图片处理部分逻辑并且使用了其在线OCR
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) 图片部分的OCR支持
- [Nonebot](https://github.com/nonebot/nonebot) 本插件运行的框架

以及，使用这个插件的你~

## 💰 赞助

**[赞助我](https://s.luochu.cc/afdian)**

<!-- AFDIAN-ACTION:START -->

<a href="https://ifdian.net/u/1122d426c63f11edb61c5254001e7c00">
    <img src="https://pic1.afdiancdn.com/default/avatar/avatar-blue.png?imageView2/1/w/120/h/120" width="40" height="40" alt="1212" title="1212"/>
</a>
<a href="https://ifdian.net/u/c35a247463a211ec953b52540025c377">
    <img src="https://pic1.afdiancdn.com/user/c35a247463a211ec953b52540025c377/avatar/802caf9c0ed80b89f943750153db6185_w1080_h1439_s1118.jpeg?imageView2/1/w/120/h/120" width="40" height="40" alt="小可爱" title="小可爱"/>
</a>
<a href="https://ifdian.net/u/0043d0507f3911f09a3b5254001e7c00">
    <img src="https://pic1.afdiancdn.com/default/avatar/avatar-purple.png?imageView2/1/w/120/h/120" width="40" height="40" alt="W" title="W"/>
</a>
<a href="https://ifdian.net/u/6220a8f04d0211eda09852540025c377">
    <img src="https://pic1.afdiancdn.com/user/user_upload_osl/7c95fbc7e6bb046e78c1d86d2fd1cb77_w132_h132_s7.jpeg?imageView2/1/w/120/h/120" width="40" height="40" alt="淡淡*清香" title="淡淡*清香"/>
</a>
<a href="https://ifdian.net/u/0daa55e2668811eda55c52540025c377">
    <img src="https://pic1.afdiancdn.com/user/user_upload_osl/fff13d28597cf85dd2188a1e6693b5b0_w132_h132_s5.jpeg?imageView2/1/w/120/h/120" width="40" height="40" alt="秋天的童话" title="秋天的童话"/>
</a>
<a href="https://ifdian.net/u/d7aa1e6457df11ea90dd52540025c377">
    <img src="https://pic1.afdiancdn.com/default/avatar/avatar-blue.png?imageView2/1/w/120/h/120" width="40" height="40" alt="爱发电用户_hYpM" title="爱发电用户_hYpM"/>
</a>
<a href="https://ifdian.net/u/2211da4a79c611edb6be52540025c377">
    <img src="https://pic1.afdiancdn.com/user/user_upload_osl/968f6bb637e3ac071e51dae506f13bc1_w132_h132_s4.jpeg?imageView2/1/w/120/h/120" width="40" height="40" alt="真" title="真"/>
</a>
<a href="https://ifdian.net/u/feceb244c29a11ebb36d52540025c377">
    <img src="https://pic1.afdiancdn.com/default/avatar/avatar-yellow.png?imageView2/1/w/120/h/120" width="40" height="40" alt="语笑嫣然" title="语笑嫣然"/>
</a>
<a href="https://ifdian.net/u/2695ae20200511efb76b52540025c377">
    <img src="https://pic1.afdiancdn.com/user/2695ae20200511efb76b52540025c377/avatar/08ab107fc95da99c2ef73853f251f760_w1080_h1072_s339.jpeg?imageView2/1/w/120/h/120" width="40" height="40" alt="Elysia" title="Elysia"/>
</a>
<a href="https://ifdian.net/u/d7168234386011eea05152540025c377">
    <img src="https://pic1.afdiancdn.com/user/user_upload_osl/53a1e9f254be6b0901a00325c7883f01_w132_h132_s5.jpeg?imageView2/1/w/120/h/120" width="40" height="40" alt="Serendipity" title="Serendipity"/>
</a>

<details>
  <summary>点我 打开/关闭 赞助者列表</summary>

<a href="https://ifdian.net/u/1122d426c63f11edb61c5254001e7c00">
1212
</a>
<span>( 0 次赞助, 共 ￥0 ) 留言: </span><br>
<a href="https://ifdian.net/u/c35a247463a211ec953b52540025c377">
小可爱
</a>
<span>( 1 次赞助, 共 ￥5 ) 留言: </span><br>
<a href="https://ifdian.net/u/0043d0507f3911f09a3b5254001e7c00">
W
</a>
<span>( 1 次赞助, 共 ￥5 ) 留言: </span><br>
<a href="https://ifdian.net/u/6220a8f04d0211eda09852540025c377">
淡淡*清香
</a>
<span>( 1 次赞助, 共 ￥9.9 ) 留言: </span><br>
<a href="https://ifdian.net/u/0daa55e2668811eda55c52540025c377">
秋天的童话
</a>
<span>( 1 次赞助, 共 ￥5 ) 留言: </span><br>
<a href="https://ifdian.net/u/d7aa1e6457df11ea90dd52540025c377">
爱发电用户_hYpM
</a>
<span>( 1 次赞助, 共 ￥5 ) 留言: </span><br>
<a href="https://ifdian.net/u/2211da4a79c611edb6be52540025c377">
真
</a>
<span>( 1 次赞助, 共 ￥5 ) 留言: </span><br>
<a href="https://ifdian.net/u/feceb244c29a11ebb36d52540025c377">
语笑嫣然
</a>
<span>( 0 次赞助, 共 ￥0 ) 留言: </span><br>
<a href="https://ifdian.net/u/2695ae20200511efb76b52540025c377">
Elysia
</a>
<span>( 1 次赞助, 共 ￥5 ) 留言: 看看腿喵</span><br>
<a href="https://ifdian.net/u/d7168234386011eea05152540025c377">
Serendipity
</a>
<span>( 1 次赞助, 共 ￥5 ) 留言: </span><br>

</details>
<!-- 注意: 尽量将标签前靠,否则经测试可能被 GitHub 解析为代码块 -->
<!-- AFDIAN-ACTION:END -->

感谢大家的赞助！你们的赞助将是我继续创作的动力！

## 📜 许可证

本项目采用 [MIT License](./LICENSE) 许可证，详情请参阅 LICENSE 文件。

## 📝 更新日志

<!-- markdownlint-disable -->
<!-- RELEASE_CHANGELOG_START -->
### 最新正式版本
- [Release 0.2.1](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/releases/tag/v0.2.1) - [v0.2.1](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/releases/tree/v0.2.1) - 2025-06-28
> # Release 0.2.1
>
> ## Feature
>
> ### Fixed
> - 修正管理和订阅指令超级用户不可用的问题 a659c208de76d7b520cffe1a17d72b578603c0c4

<!-- RELEASE_CHANGELOG_END -->
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<!-- PRERELEASE_CHANGELOG_START -->

<!-- PRERELEASE_CHANGELOG_END -->
<!-- markdownlint-enable -->

更多Release请见 [Releases](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/releases)

完整更新日志请见 [CHANGELOG.md](./CHANGELOG.md)
