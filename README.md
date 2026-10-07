# Antigravity-Clash

English | [简体中文](README.zh-CN.md)

Launch Antigravity through Clash Verge without enabling the macOS system proxy or TUN mode.

## Requirements

- macOS 13 or later.
- Antigravity installed at `/Applications/Antigravity.app`.
- Clash Verge running with its mixed port at `127.0.0.1:7897`.

## Install and use

```sh
./install.sh
open "$HOME/Applications/Antigravity-Clash.app"
```

The installer puts the app in `~/Applications` and the command-line launcher at `~/.local/bin/antigravity-clash`. You can also run `bin/antigravity-clash` directly from a terminal.

The launcher checks the Clash port and the Antigravity main process. If an existing instance lacks the expected proxy environment, it asks you to quit Antigravity completely and try again. After starting a new instance, it verifies the proxy environment. A file lock prevents repeated clicks from starting multiple instances.

## Direct connections

`localhost`, `127.0.0.1`, and `::1` bypass the proxy by default. To add domains, put a single comma-separated line in `~/.config/antigravity-clash/no-proxy`, for example:

```text
.example.com,.internal.example
```

This file stays on your machine and is not bundled with the app. Processes launched by Antigravity, including its integrated terminal and extensions, inherit the proxy environment. Clash rules determine whether each request ultimately uses a proxy or a direct connection.

## Source files

| Path | Purpose |
| --- | --- |
| `bin/antigravity-clash` | Launch and process checks |
| `app/Contents/MacOS/Antigravity-Clash` | Dock entry point and error dialog |
| `app/Contents/Info.plist` | macOS app metadata |
| `app/Contents/Resources/AppIcon.icns` | App icon |
| `install.sh` | Install the command-line launcher, assemble the app, and sign it |

The installer creates a local ad hoc signature; signature files are not committed. This project is licensed under the [MIT License](LICENSE).
