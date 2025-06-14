# 📝 更新日志

<a id="v0.2.0a1"></a>
## [Release 0.2.0a1 (v0.2.0a1)](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/releases/tag/v0.2.0a1) - 2025-06-07

> [!WARNING]
> 此版本为预发行版，未通过充分测试，仅建议追求最新功能用户尝试

## Feature

### Added
- 支持分群可选是否启用插件(仅data) [`be8b6d89b7`](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/commit/be8b6d89b711209bf2495283719f02ef5d52530f)
  - 此功能仅在data.json中可用，目前不在可配置项中提供，未设置此项的群默认不启用插件
  - 启用插件需要bot在群聊，且具有管理权限的成员使用指令开启

### Changed
- 现在判定用户尝试管理类指令但不具备管理权限时，不再对指令进行答复 [`5c9978bf40`](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/commit/5c9978bf4050ebac7109a1990fc04c4154644d46)
  - 此前版本会在用户不具备权限时回复`您不是这个群的管理员哦~`，如果有用户频繁使用指令可能导致机器人风控
  - 后续预计修改成一段时间内仅进行一次不具备权限回复

## CI/CD
- 增加自动changelog更新 [`7cee04957c`](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/commit/7cee04957c0dbcc6ea1e89cc65c264fb90c447da)

**Full Changelog**: https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/compare/v0.1.9...v0.2.0a1

[Changes][v0.2.0a1]


<a id="v0.1.9"></a>
## [Release 0.1.9 (v0.1.9)](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/releases/tag/v0.1.9) - 2025-05-01

**上架商店啦🎉🎉🎉**

## Feature

### Added
- 对图片进行 OCR 识别
- 对文本进行模糊匹配
- 排除字符对识别影响，如"代.理"
- 支持自定义词库
- 支持管理员/群主私聊订阅禁言通知
- 支持自定义禁言时间

**Full Changelog**: https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/compare/Init...v0.1.9

[Changes][v0.1.9]


[v0.2.0a1]: https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/compare/v0.1.9...v0.2.0a1
[v0.1.9]: https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/tree/v0.1.9

<!-- Generated by https://github.com/rhysd/changelog-from-release v3.9.0 -->

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

