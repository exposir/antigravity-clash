# Sourced at the end of the user's zsh login file. Only the app's capture shell
# receives these exports; ordinary terminals and other apps keep their env.
() {
  [[ -o interactive && -o login ]] || return 0
  local agc_parent agc_exports
  agc_parent=$(/bin/ps -p "$PPID" -o comm= 2>/dev/null) || return 0
  [[ "$agc_parent" == /Applications/Antigravity.app/Contents/MacOS/Antigravity ]] || return 0
  agc_exports=$("$HOME/.local/bin/antigravity-clash" --shell-env) || return 0
  eval "$agc_exports"
}
