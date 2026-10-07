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

The launcher checks the Clash port and the Antigravity process tree. It accepts a main process with the expected proxy environment or its own language server with that environment. It waits up to 10 seconds for startup and asks you to quit completely if the environment is missing. A file lock prevents repeated clicks from starting multiple instances.

## Launch from the original Antigravity icon

**Experimental:** shell environment injection and process isolation have been verified on Antigravity 2.19.1. Login and AI requests after a cold launch from the original icon have not yet been verified end to end.

For macOS users whose default shell is zsh:

```sh
./install.sh --direct-launch
```

Quit Antigravity completely once, keep Clash running, then launch from the original Antigravity icon. The installer adds one managed block at the end of `.zlogin` in your zsh configuration directory, respecting `ZDOTDIR`. Existing files are backed up in `~/.config/antigravity-clash/`. Reinstalling replaces the managed block.

The hook matches the full executable path of the shell's immediate parent. When Antigravity reads its shell environment, it injects the same proxy variables and bypass domains as the launcher. Ordinary terminals and other apps do not trigger the hook. The proxy remains configured when Clash is stopped; start Clash to restore connectivity.

This mode was checked against Antigravity 2.19.1. It depends on Antigravity reading its shell environment and covers its language server and descendants. It does not configure the main process, updater, or browser. App updates or shell changes can affect compatibility. Check the actual backend state with:

```sh
antigravity-clash --status
```

This reports the local port, backend proxy environment, and established connections to Clash. An idle backend may have no active connections.

Once this mode is enabled, you can remove `~/Applications/Antigravity-Clash.app` and its Dock icon. Keep `~/.local/bin/antigravity-clash`, the files in `~/.config/antigravity-clash/`, and the managed `.zlogin` block: direct launch still uses these dependencies.

To disable this mode while retaining the launcher:

```sh
./direct-launch.sh disable
```

Restart Antigravity after enabling or disabling this mode. Existing processes keep their environment until they exit. Compiled `.zlogin.zwc` files must be removed or rebuilt before installation.

## Direct connections

`localhost`, `127.0.0.1`, and `::1` bypass the proxy by default. To add domains, put a single comma-separated line in `~/.config/antigravity-clash/no-proxy`, for example:

```text
.example.com,.internal.example
```

This file stays on your machine and is not bundled with the app. Children of a proxied process, including agent tasks and MCP servers, can inherit the proxy environment. Clash rules determine whether each request ultimately uses a proxy or a direct connection. Restart Antigravity after changing bypass domains.

## Source files

| Path | Purpose |
| --- | --- |
| `bin/antigravity-clash` | Launch and process checks |
| `app/Contents/MacOS/Antigravity-Clash` | Dock entry point and error dialog |
| `app/Contents/Info.plist` | macOS app metadata |
| `app/Contents/Resources/AppIcon.icns` | App icon |
| `install.sh` | Install the command-line launcher, assemble the app, and sign it |
| `direct-launch.sh` | Enable or disable the managed zsh login hook |
| `shell/direct-launch.zsh` | Inject proxy variables into Antigravity's environment-capture shell |

The installer creates a local ad hoc signature; signature files are not committed. This project is licensed under the [MIT License](LICENSE).
