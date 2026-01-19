# 📝 更新日志

<a id="v0.4.0"></a>
## [v0.4.0](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/releases/tag/v0.4.0) - 2026-01-19

> [!WARNING]
> ## 破坏性变更 | BREAKING CHANGE
> 由于依赖安全性问题，不再支持Python 3.9
> 目前 **最低版本Python 3.10**

# 当前版本与上一版本无功能变更，Python3.9用户请勿更新此版本

## CI/CD
- 发布工作流整合入组织仓库 [`87b901e494`](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/commit/87b901e4949a7473e724a510ce324bf21e8f88df)
- 增加爱发电打赏用户感谢列表 [`87b901e494`](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/commit/87b901e4949a7473e724a510ce324bf21e8f88df)

## Dependence
- 更新Python最低版本为3.10 [`9a30fb3f16`](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/commit/9a30fb3f16b24ecc632d47c2008a9bdbd98e0e1f)
- 更新了一堆依赖 [#37](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/issues/37) [#38](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/issues/38) [#39](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/issues/39) [#40](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/issues/40) [#41](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/issues/41) [#42](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/issues/42) 

**Full Changelog**: https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/compare/v0.2.1...v0.4.0

[Changes][v0.4.0]


<a id="v0.2.1"></a>
## [Release 0.2.1 (v0.2.1)](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/releases/tag/v0.2.1) - 2025-06-28

## Feature

### Fixed
- 修正管理和订阅指令超级用户不可用的问题 [`a659c208de`](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/commit/a659c208de76d7b520cffe1a17d72b578603c0c4)


**Full Changelog**: https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/compare/v0.2.0...v0.2.1

[Changes][v0.2.1]


<a id="v0.2.0"></a>
## [Release 0.2.0 (v0.2.0)](https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/releases/tag/v0.2.0) - 2025-06-28

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
- 从Poetry换uv管理，修复了一系列workflow问题 https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/compare/be3f97afab2074d5dd8cbd0f6f2e7e4aaa2e83c1...38a4d58ef82c88eb9cc48bafed4636f833ebec2c


**Full Changelog**: https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/compare/v0.1.9...v0.2.0

[Changes][v0.2.0]


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


[v0.4.0]: https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/compare/v0.2.1...v0.4.0
[v0.2.1]: https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/compare/v0.2.0...v0.2.1
[v0.2.0]: https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/compare/v0.2.0a1...v0.2.0
[v0.2.0a1]: https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/compare/v0.1.9...v0.2.0a1
[v0.1.9]: https://github.com/LuoChu-NB2Dev/nonebot-plugin-noadpls/tree/v0.1.9

<!-- Generated by https://github.com/rhysd/changelog-from-release v3.9.1 -->

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

