"""Small local file browser/editor for the aderrr workspace."""

from __future__ import annotations

import json
import mimetypes
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
IGNORED = {".git", ".venv", "__pycache__", ".pytest_cache"}


def safe_path(value: str) -> Path:
    candidate = (ROOT / value).resolve()
    if candidate != ROOT and ROOT not in candidate.parents:
        raise ValueError("path outside project")
    return candidate


def files() -> list[str]:
    result = []
    for path in ROOT.rglob("*"):
        if any(part in IGNORED for part in path.parts):
            continue
        if path.is_file():
            result.append(path.relative_to(ROOT).as_posix())
    return sorted(result)


PAGE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>aderrr 编辑环境</title><style>
*{box-sizing:border-box}body{margin:0;height:100vh;display:flex;background:#111827;color:#e5e7eb;font:14px system-ui,sans-serif}
aside{width:280px;border-right:1px solid #374151;padding:18px;overflow:auto}main{flex:1;display:flex;flex-direction:column;min-width:0}
h1{font-size:18px;margin:0 0 16px}.file{display:block;width:100%;padding:8px 10px;border:0;border-radius:6px;background:transparent;color:#d1d5db;text-align:left;cursor:pointer}.file:hover,.file.active{background:#374151;color:#fff}
header{display:flex;align-items:center;gap:12px;padding:14px 18px;border-bottom:1px solid #374151}#path{flex:1;color:#9ca3af}button{border:0;border-radius:6px;padding:8px 14px;background:#2563eb;color:#fff;cursor:pointer}button:disabled{opacity:.5;cursor:wait}
textarea{flex:1;width:100%;resize:none;border:0;outline:0;padding:20px;background:#0b1220;color:#e5e7eb;font:14px ui-monospace,SFMono-Regular,Consolas,monospace;line-height:1.5}#status{color:#9ca3af;font-size:12px}
#console{height:190px;border-top:1px solid #374151;background:#070d18;padding:10px 18px}.actions{display:flex;gap:8px}.actions button{background:#374151;font-size:12px}#output{height:125px;overflow:auto;margin:8px 0;color:#a7f3d0;font:12px ui-monospace,monospace;white-space:pre-wrap}
</style></head><body><aside><h1>aderrr 文件</h1><div id="files">加载中…</div></aside><main><header><span id="path">选择一个文件</span><span id="status"></span><button id="save" disabled>保存</button></header><textarea id="editor" spellcheck="false" disabled></textarea><section id="console"><div class="actions"><button onclick="run('test')">运行测试</button><button onclick="run('compile')">编译检查</button><button onclick="run('app')">运行程序</button></div><pre id="output">运行结果会显示在这里</pre></section></main>
<script>
const filesEl=document.querySelector('#files'), editor=document.querySelector('#editor'), pathEl=document.querySelector('#path'), statusEl=document.querySelector('#status'), save=document.querySelector('#save'); let current='';
async function loadFiles(){const r=await fetch('/api/files');const list=await r.json();filesEl.innerHTML='';list.forEach(name=>{const b=document.createElement('button');b.className='file';b.textContent=name;b.onclick=()=>openFile(name,b);filesEl.appendChild(b)})}
async function openFile(name,button){const r=await fetch('/api/file?path='+encodeURIComponent(name));const data=await r.json();current=name;editor.value=data.content;editor.disabled=false;save.disabled=false;pathEl.textContent=name;statusEl.textContent='';document.querySelectorAll('.file').forEach(x=>x.classList.remove('active'));button.classList.add('active')}
save.onclick=async()=>{save.disabled=true;const r=await fetch('/api/file',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:current,content:editor.value})});const data=await r.json();statusEl.textContent=data.ok?'已保存':'保存失败';save.disabled=false}
async function run(action){const output=document.querySelector('#output');output.textContent='运行中…';const r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action})});const data=await r.json();output.textContent=data.output||data.error||'无输出'}
loadFiles();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def send_json(self, value: object, status: int = 200) -> None:
        body = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/":
                body = PAGE.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif parsed.path == "/api/files":
                self.send_json(files())
            elif parsed.path == "/api/file":
                name = parse_qs(parsed.query).get("path", [""])[0]
                path = safe_path(name)
                self.send_json({"path": name, "content": path.read_text(encoding="utf-8")})
            else:
                self.send_error(404)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            self.send_json({"error": str(exc)}, 400)

    def do_PUT(self) -> None:  # noqa: N802
        if self.path != "/api/file":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length))
            path = safe_path(str(data["path"]))
            if not path.is_file():
                raise ValueError("file does not exist")
            path.write_text(str(data["content"]), encoding="utf-8")
            self.send_json({"ok": True})
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self.send_json({"ok": False, "error": str(exc)}, 400)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/run":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            action = json.loads(self.rfile.read(length)).get("action")
            commands = {
                "test": [".venv/bin/python", "-m", "unittest", "discover", "-s", "tests", "-v"],
                "compile": [".venv/bin/python", "-m", "py_compile", "tools/editor_server.py"],
                "app": [".venv/bin/python", "-m", "aderrr"],
            }
            if action not in commands:
                raise ValueError("unsupported action")
            result = subprocess.run(commands[action], cwd=ROOT, capture_output=True, text=True, timeout=30)
            self.send_json({"ok": result.returncode == 0, "output": result.stdout + result.stderr, "returncode": result.returncode})
        except (OSError, subprocess.TimeoutExpired, TypeError, ValueError, json.JSONDecodeError) as exc:
            self.send_json({"ok": False, "error": str(exc)}, 400)

    def log_message(self, *_: object) -> None:
        pass


def main() -> None:
    port = int(os.environ.get("PORT", os.environ.get("ADERRR_EDITOR_PORT", "8765")))
    host = os.environ.get("ADERRR_EDITOR_HOST", "127.0.0.1")
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"aderrr editor: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
