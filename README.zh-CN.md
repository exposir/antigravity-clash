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

启动器会检查 Clash 端口及 Antigravity 主进程。已有实例若没有预期的代理变量，会提示完全退出后重试；新实例启动后会核对代理变量。连续点击图标时使用文件锁避免重复启动。

## 直连域名

默认直连 `localhost`、`127.0.0.1` 和 `::1`。如需添加域名，在 `~/.config/antigravity-clash/no-proxy` 写入一行逗号分隔的域名，例如：

```text
.example.com,.internal.example
```

该文件只保存在本机，不会打包进应用。代理变量也会被 Antigravity 启动的子进程继承，包括内置终端和扩展。Clash 的规则决定请求最终是代理还是直连。

## 源码

| 路径 | 用途 |
| --- | --- |
| `bin/antigravity-clash` | 启动与检查逻辑 |
| `app/Contents/MacOS/Antigravity-Clash` | Dock 入口和错误对话框 |
| `app/Contents/Info.plist` | macOS 应用元数据 |
| `app/Contents/Resources/AppIcon.icns` | 应用图标 |
| `install.sh` | 安装命令行入口并组装、签名应用包 |

应用包使用本机临时签名，签名产物不纳入仓库。项目采用 [MIT License](LICENSE)。
