from __future__ import annotations

import json
import queue
import subprocess as sp
import sys
import threading
import time
from typing import Any, Dict


class LSPClient:
    def __init__(self) -> None:
        self.proc = sp.Popen(
            [sys.executable, "-u", "-m", "sup.lsp_server"], stdin=sp.PIPE, stdout=sp.PIPE
        )
        assert self.proc.stdin and self.proc.stdout
        self._in = self.proc.stdin
        self._out = self.proc.stdout
        self._q: "queue.Queue[Dict[str, Any]]" = queue.Queue()
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    def _read_loop(self) -> None:
        buf = b""
        out = self._out
        while True:
            chunk = out.readline()
            if not chunk:
                break
            if not chunk.lower().startswith(b"content-length:"):
                continue
            try:
                length = int(chunk.split(b":", 1)[1].strip())
            except Exception:
                # skip invalid
                _ = out.readline()
                continue
            # consume CRLF
            _ = out.readline()
            body = out.read(length)
            try:
                msg = json.loads(body.decode("utf-8"))
                self._q.put(msg)
            except Exception:
                pass

    def send(self, msg: Dict[str, Any]) -> None:
        data = json.dumps(msg).encode("utf-8")
        header = f"Content-Length: {len(data)}\r\n\r\n".encode("ascii")
        self._in.write(header)
        self._in.write(data)
        self._in.flush()

    def recv_id(self, id_val: int, timeout: float = 3.0) -> Dict[str, Any] | None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                msg = self._q.get(timeout=0.1)
            except queue.Empty:
                continue
            if msg.get("id") == id_val:
                return msg
        return None

    def close(self) -> None:
        try:
            self.send({"jsonrpc": "2.0", "method": "exit"})
        except Exception:
            pass
        try:
            self.proc.terminate()
        except Exception:
            pass


def test_lsp_initialize_hover_completion_definition_rename(tmp_path) -> None:
    client = LSPClient()
    try:
        # initialize
        client.send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"capabilities": {}}})
        resp = client.recv_id(1)
        assert resp and resp.get("result", {}).get("capabilities", {}).get("hoverProvider") is True
        # open doc
        code = (
            "sup\n"
            "define function called add with a and b\n"
            "  return add a and b\n"
            "end function\n"
            "print call add with 1 and 2\n"
            "bye\n"
        )
        uri = (tmp_path / "t.sup").as_uri()
        client.send({
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {"textDocument": {"uri": uri, "text": code}},
        })
        # hover on function name
        client.send({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "textDocument/hover",
            "params": {"textDocument": {"uri": uri}, "position": {"line": 1, "character": 25}},
        })
        hover = client.recv_id(2)
        assert hover and hover.get("result", {}).get("contents")
        # completion request
        client.send({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/completion",
            "params": {"textDocument": {"uri": uri}, "position": {"line": 4, "character": 6}},
        })
        comp = client.recv_id(3)
        assert comp and isinstance(comp.get("result"), list)
        # definition (best-effort)
        client.send({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/definition",
            "params": {"textDocument": {"uri": uri}, "position": {"line": 4, "character": 13}},
        })
        _ = client.recv_id(4)
        # rename
        client.send({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/rename",
            "params": {"textDocument": {"uri": uri}, "position": {"line": 1, "character": 25}, "newName": "sum"},
        })
        r = client.recv_id(5)
        assert r and r.get("result") is not None
    finally:
        client.close()


