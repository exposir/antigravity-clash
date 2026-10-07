# Antigravity-Clash

[English](README.md) | 简体中文

在不启用 macOS 系统代理或 TUN 模式的情况下，为 Antigravity 单独设置 Clash Verge 代理。

## 前提

- macOS 13 或更新版本。
- Antigravity 安装在 `/Applications/Antigravity.app`。
- Clash Verge 正在运行，mixed port 为 `127.0.0.1:7897`。

## 安装与使用

```sh
./install.sh
open "$HOME/Applications/Antigravity-Clash.app"
```

安装脚本将应用放在 `~/Applications`，并将命令行入口放在 `~/.local/bin/antigravity-clash`。也可以直接从终端运行 `bin/antigravity-clash`。

启动器会检查 Clash 端口及 Antigravity 进程树。主进程带有预期代理，或其自身的后台服务带有预期代理，都可以识别。启动时最多等待 10 秒，环境不正确时提示完全退出后重试。连续点击图标时使用文件锁避免重复启动。

## 直接点击原版 Antigravity 图标

**实验功能：**已在 Antigravity 2.19.1 验证 Shell 环境注入和进程隔离；从原版图标冷启动后的登录与 AI 请求尚未完成端到端验证。

macOS 的默认 Shell 为 zsh 时，可以启用：

```sh
./install.sh --direct-launch
```

完全退出 Antigravity 一次，保持 Clash 运行，然后直接点击原版图标。安装器会在 zsh 配置目录的 `.zlogin` 末尾添加一个受管理的配置块，支持 `ZDOTDIR`。已有文件会备份到 `~/.config/antigravity-clash/`，重复安装会替换该配置块。

配置只匹配 Shell 直接父进程的完整可执行路径。反重力读取 Shell 环境时，注入与启动器相同的代理变量和直连域名；普通终端和其他应用不会触发。Clash 停止时仍保留代理配置，重新启动 Clash 后才能恢复网络访问。

此模式已针对 Antigravity 2.19.1 检查，依赖反重力读取 Shell 环境，覆盖后台服务及其子进程。主进程、更新器和浏览器不由这条配置设置代理。应用更新或更换 Shell 后可能需要重新检查兼容性。查看实际后台状态：

```sh
antigravity-clash --status
```

命令显示本地端口、后台代理环境和到 Clash 的已建立连接；空闲时没有活动连接可能正常。

启用此模式后，可以删除 `~/Applications/Antigravity-Clash.app` 和它的 Dock 图标。请保留 `~/.local/bin/antigravity-clash`、`~/.config/antigravity-clash/` 下的文件及 `.zlogin` 中的受管理配置块，原版直接启动仍依赖这些文件。

禁用此模式并保留启动器：

```sh
./direct-launch.sh disable
```

启用、禁用后需要重启 Antigravity，已有进程会保留原来的环境。安装前需移除或重新生成已编译的 `.zlogin.zwc` 文件。

## 直连域名

默认直连 `localhost`、`127.0.0.1` 和 `::1`。如需添加域名，在 `~/.config/antigravity-clash/no-proxy` 写入一行逗号分隔的域名，例如：

```text
.example.com,.internal.example
```

该文件只保存在本机，不会打包进应用。带有代理的进程所启动的子进程，包括 AI 任务和 MCP 服务，也可能继承代理变量。Clash 的规则决定请求最终是代理还是直连。修改直连域名后需重启 Antigravity。

## 源码

| 路径 | 用途 |
| --- | --- |
| `bin/antigravity-clash` | 启动与检查逻辑 |
| `app/Contents/MacOS/Antigravity-Clash` | Dock 入口和错误对话框 |
| `app/Contents/Info.plist` | macOS 应用元数据 |
| `app/Contents/Resources/AppIcon.icns` | 应用图标 |
| `install.sh` | 安装命令行入口并组装、签名应用包 |
| `direct-launch.sh` | 启用或禁用受管理的 zsh 登录配置 |
| `shell/direct-launch.zsh` | 为反重力读取 Shell 环境的调用注入代理变量 |

应用包使用本机临时签名，签名产物不纳入仓库。项目采用 [MIT License](LICENSE)。
