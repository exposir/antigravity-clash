import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROXY = "http://127.0.0.1:7897"
SOCKS = "socks5h://127.0.0.1:7897"
STUB = r'''#!/usr/bin/python3
import json, os, sys
from pathlib import Path
tool = Path(sys.argv[0]).name
p = Path(os.environ['AGC_TEST_STATE'])
s = json.loads(p.read_text())
args = sys.argv[1:]
if tool == 'nc':
    sys.exit(0 if s.get('port', True) else 1)
if tool == 'pgrep':
    if s.get('process_error'):
        sys.exit(2)
    if '-P' in args:
        parent = args[args.index('-P') + 1]
        ready = s.get('ticks', 0) >= s.get('server_after', 0)
        ids = s.get('servers', []) if parent == '101' and ready else []
    else:
        if 'language_server' in args[-1]:
            ids = s.get('unrelated_servers', [])
        else:
            ids = [101] if s.get('existing', True) or s.get('launched') else []
    for pid in ids:
        print(pid)
    sys.exit(0 if ids else 1)
if tool == 'ps':
    pid = args[args.index('-p') + 1]
    proxied = s.get('main_proxy', False) if pid == '101' else s.get('server_proxy', False)
    if proxied:
        print('HTTP_PROXY=http://127.0.0.1:7897 HTTPS_PROXY=http://127.0.0.1:7897 ALL_PROXY=socks5h://127.0.0.1:7897')
    else:
        print('HTTP_PROXY=http://127.0.0.1:78970 HTTPS_PROXY=none ALL_PROXY=none')
if tool == 'open':
    s.setdefault('opens', []).append(args)
    s['launched'] = True
    p.write_text(json.dumps(s))
    sys.exit(s.get('open_rc', 0))
if tool == 'sleep':
    s['ticks'] = s.get('ticks', 0) + 1
    p.write_text(json.dumps(s))
if tool == 'lsof':
    sys.exit(0 if s.get('connection') else 1)
if tool == 'head':
    print(s.get('extra_no_proxy', '.example.com'))
'''


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agc-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.mock_bin = self.base / "bin"
        self.mock_bin.mkdir()
        for tool in ["pgrep", "ps", "nc", "open", "sleep", "lsof", "head"]:
            p = self.mock_bin / tool
            p.write_text(STUB)
            p.chmod(0o755)
        self.state = self.base / "state.json"
        self.env = dict(os.environ, PATH=f"{self.mock_bin}:/usr/bin:/bin", AGC_TEST_STATE=str(self.state))

    def run_launcher(self, state, option="--locked"):
        self.state.write_text(json.dumps(state))
        result = subprocess.run(["/bin/zsh", str(ROOT / "bin/antigravity-clash"), option],
                                env=self.env, text=True, capture_output=True, timeout=15)
        return result, json.loads(self.state.read_text())

    def test_existing_main_proxy_still_works(self):
        r, s = self.run_launcher({"main_proxy": True})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(s["opens"][0][0], "-a")

    def test_direct_backend_proxy_is_accepted(self):
        r, s = self.run_launcher({"servers": [201], "server_proxy": True})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(s["opens"][0][0], "-a")

    def test_waits_for_direct_backend(self):
        r, s = self.run_launcher({"servers": [201], "server_proxy": True, "server_after": 2})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(s["ticks"], 2)

    def test_wrong_backend_is_rejected_even_with_proxied_main(self):
        r, s = self.run_launcher({"main_proxy": True, "servers": [201]})
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("opens", s)

    def test_no_proxy_does_not_open_existing_app(self):
        r, s = self.run_launcher({})
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("opens", s)

    def test_other_parent_backend_is_not_accepted(self):
        r, s = self.run_launcher({"servers": [], "unrelated_servers": [301], "server_proxy": True})
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("opens", s)

    def test_clash_offline_does_not_launch(self):
        r, s = self.run_launcher({"port": False})
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("opens", s)

    def test_open_failure_is_preserved(self):
        r, _ = self.run_launcher({"main_proxy": True, "open_rc": 7})
        self.assertEqual(r.returncode, 7)

    def test_fresh_launch_injects_proxy(self):
        r, s = self.run_launcher({"existing": False, "main_proxy": True})
        self.assertEqual(r.returncode, 0, r.stderr)
        args = s["opens"][0]
        self.assertEqual(args[0], "-na")
        self.assertIn(f"HTTP_PROXY={PROXY}", args)
        self.assertIn(f"ALL_PROXY={SOCKS}", args)

    def test_process_lookup_error_does_not_launch(self):
        r, s = self.run_launcher({"process_error": True})
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("opens", s)

    def test_fresh_launch_reports_proxy_failure_after_process_appears(self):
        r, s = self.run_launcher({"existing": False})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("未确认预期代理", r.stderr)
        self.assertEqual(len(s["opens"]), 1)

    def test_status_checks_backend_without_launching(self):
        r, s = self.run_launcher({"servers": [201], "server_proxy": True, "connection": True}, "--status")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("已建立到 Clash", r.stdout)
        self.assertNotIn("opens", s)

    def test_status_rejects_missing_backend(self):
        r, s = self.run_launcher({"main_proxy": True}, "--status")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("opens", s)

    def test_shell_exports_work_when_clash_is_offline(self):
        r, s = self.run_launcher({"port": False, "process_error": True}, "--shell-env")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("opens", s)
        command = r.stdout + '\n[[ "$HTTP_PROXY" == "http://127.0.0.1:7897" && "$ALL_PROXY" == "socks5h://127.0.0.1:7897" ]]'
        checked = subprocess.run(["/bin/zsh", "-f", "-c", command], capture_output=True)
        self.assertEqual(checked.returncode, 0)

    def test_bypass_domains_are_data_not_shell_commands(self):
        if not (Path.home() / ".config/antigravity-clash/no-proxy").exists():
            self.skipTest("requires an existing bypass file to exercise its reader")
        marker = self.base / "unexpected-execution"
        payload = f".example.com,$(touch${{IFS}}{marker})"
        r, _ = self.run_launcher({"extra_no_proxy": payload}, "--shell-env")
        self.assertEqual(r.returncode, 0)
        checked = subprocess.run(["/bin/zsh", "-f", "-c", r.stdout], capture_output=True)
        self.assertEqual(checked.returncode, 0)
        self.assertFalse(marker.exists())


class LoginConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agc-login-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.zdotdir = self.base / "zsh with spaces"
        self.zdotdir.mkdir()
        self.config = self.base / "config with spaces"
        self.zlogin = self.zdotdir / ".zlogin"
        self.original = "export UNRELATED_MARKER=keep\n"
        self.zlogin.write_text(self.original)
        self.env = dict(os.environ, ZDOTDIR=str(self.zdotdir),
                        ANTIGRAVITY_CLASH_CONFIG_DIR=str(self.config))

    def manage(self, action):
        return subprocess.run(["/bin/zsh", str(ROOT / "direct-launch.sh"), action],
                              env=self.env, text=True, capture_output=True, timeout=20)

    def test_enable_is_idempotent_and_disable_preserves_content(self):
        first = self.manage("enable")
        self.assertEqual(first.returncode, 0, first.stderr)
        enabled = self.zlogin.read_text()
        self.assertTrue(enabled.startswith(self.original))
        self.assertEqual(self.manage("enable").returncode, 0)
        self.assertEqual(self.zlogin.read_text(), enabled)
        check = subprocess.run(["/bin/zsh", "-n", str(self.zlogin)], capture_output=True)
        self.assertEqual(check.returncode, 0)
        self.assertEqual(self.manage("disable").returncode, 0)
        self.assertEqual(self.zlogin.read_text(), self.original)
        self.assertFalse((self.config / "direct-launch.zsh").exists())
        self.assertEqual(self.manage("disable").returncode, 0)

    def test_symlink_is_preserved(self):
        target = self.base / "actual-login"
        target.write_text(self.original)
        self.zlogin.unlink()
        self.zlogin.symlink_to(target)
        self.assertEqual(self.manage("enable").returncode, 0)
        self.assertTrue(self.zlogin.is_symlink())
        self.assertEqual(self.manage("disable").returncode, 0)
        self.assertEqual(target.read_text(), self.original)

    def test_incomplete_managed_block_is_not_rewritten(self):
        text = self.original + "# >>> antigravity-clash direct launch >>>\n"
        self.zlogin.write_text(text)
        r = self.manage("enable")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.zlogin.read_text(), text)

    def test_compiled_login_configuration_is_rejected(self):
        self.zlogin.with_name(".zlogin.zwc").write_bytes(b"cache")
        self.assertNotEqual(self.manage("enable").returncode, 0)
        self.assertEqual(self.zlogin.read_text(), self.original)

    def test_unmatched_end_marker_is_not_rewritten(self):
        text = self.original + "# <<< antigravity-clash direct launch <<<\n"
        self.zlogin.write_text(text)
        self.assertNotEqual(self.manage("enable").returncode, 0)
        self.assertEqual(self.zlogin.read_text(), text)


if __name__ == "__main__":
    unittest.main()
