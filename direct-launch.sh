#!/bin/zsh
set -e

ROOT=${0:A:h}
CONFIG_DIR=${ANTIGRAVITY_CLASH_CONFIG_DIR:-$HOME/.config/antigravity-clash}
BEGIN_MARKER='# >>> antigravity-clash direct launch >>>'
END_MARKER='# <<< antigravity-clash direct launch <<<'

strip_block() {
  /usr/bin/awk -v begin="$BEGIN_MARKER" -v end="$END_MARKER" '
    $0 == begin { if (inside) exit 1; inside = 1; next }
    $0 == end { if (!inside) exit 1; inside = 0; next }
    !inside { print }
    END { if (inside) exit 1 }
  ' "$1"
}

case "${1:-}" in
  enable)
    user_shell=$(/usr/bin/dscl . -read "/Users/$(id -un)" UserShell | /usr/bin/awk '{print $2}')
    if [[ "${user_shell:t}" != zsh ]]; then
      echo "错误: 原版直接启动模式目前仅支持默认 Shell 为 zsh；请使用启动器" >&2
      exit 1
    fi
    if [[ -n "${ZDOTDIR:-}" ]]; then
      zlogin_dir=$ZDOTDIR
    else
      zlogin_dir=$(/bin/zsh -lic 'print -r -- "ANTIGRAVITY_CLASH_ZDOTDIR=${ZDOTDIR:-$HOME}"' |
        /usr/bin/sed -n 's/^ANTIGRAVITY_CLASH_ZDOTDIR=//p' | /usr/bin/tail -n 1)
    fi
    [[ -n "$zlogin_dir" && "$zlogin_dir" == /* ]] || { echo "错误: 无法确定 zsh 配置目录" >&2; exit 1; }
    zlogin_path="${zlogin_dir}/.zlogin"
    zlogin_path=${zlogin_path:A}
    if [[ -f "$CONFIG_DIR/zlogin-path" && "$(<"$CONFIG_DIR/zlogin-path")" != "$zlogin_path" ]]; then
      echo "错误: zsh 配置目录已改变，请先执行 ./direct-launch.sh disable 再启用" >&2
      exit 1
    fi
    if [[ -e "$zlogin_path.zwc" ]]; then
      echo "错误: 存在已编译的 $zlogin_path.zwc，请先移除编译缓存再启用" >&2
      exit 1
    fi
    mkdir -p "$CONFIG_DIR" "${zlogin_path:h}"
    install -m 644 "$ROOT/shell/direct-launch.zsh" "$CONFIG_DIR/direct-launch.zsh"
    ;;
  disable)
    if [[ ! -r "$CONFIG_DIR/zlogin-path" ]]; then
      echo "原版直接启动模式未启用"
      exit 0
    fi
    zlogin_path=$(<"$CONFIG_DIR/zlogin-path")
    ;;
  *)
    echo "用法: ./direct-launch.sh enable|disable" >&2
    exit 2
    ;;
esac

temporary=$(mktemp "${zlogin_path:h}/.antigravity-clash.XXXXXX")
trap 'rm -f "$temporary"' EXIT
if [[ -e "$zlogin_path" ]]; then
  backup=$(mktemp "$CONFIG_DIR/zlogin.backup.XXXXXX")
  cp -p "$zlogin_path" "$backup"
  cp -p "$zlogin_path" "$temporary"
  if ! strip_block "$zlogin_path" > "$temporary"; then
    echo "错误: 启动配置标记不完整，已保留原文件；备份: $backup" >&2
    exit 1
  fi
fi

if [[ "$1" == enable ]]; then
  print -r -- "$BEGIN_MARKER" >> "$temporary"
  print -r -- "[[ ! -r ${(q)CONFIG_DIR}/direct-launch.zsh ]] || source ${(q)CONFIG_DIR}/direct-launch.zsh" >> "$temporary"
  print -r -- "$END_MARKER" >> "$temporary"
fi
mv -f "$temporary" "$zlogin_path"
if [[ "$1" == enable ]]; then
  print -r -- "$zlogin_path" > "$CONFIG_DIR/zlogin-path"
  chmod 600 "$CONFIG_DIR/zlogin-path"
  echo "原版直接启动模式已启用: $zlogin_path"
  echo "完全退出 Antigravity 后，可直接点击原版图标；Clash 必须保持运行"
else
  rm -f "$CONFIG_DIR/direct-launch.zsh" "$CONFIG_DIR/zlogin-path"
  echo "原版直接启动模式已禁用；启动器仍可使用"
fi
