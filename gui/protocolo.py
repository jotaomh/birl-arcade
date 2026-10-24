"""Ponte entre a interface GTK4 e o cerebro BIRL.

O BIRL roda como processo filho e conversa por linhas de texto.
Este modulo so cuida de processo/pipe; nenhuma regra de jogo vive aqui.
"""

from __future__ import annotations

import os
import shutil
import subprocess

from gi.repository import GLib, GObject


class MotorBirl(GObject.Object):
    __gsignals__ = {
        "linha": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "fim": (GObject.SignalFlags.RUN_FIRST, None, (int,)),
        "erro": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, raiz: str, jogo: str, extras: dict[str, str] | None = None):
        super().__init__()
        self.raiz = raiz
        self.jogo = jogo
        self._buffer = b""
        self._erro_buffer = b""
        self._watches: list[int] = []
        self.proc: subprocess.Popen[bytes] | None = None

        node = shutil.which("node") or "node"
        script = os.path.join(raiz, "node_modules", "birl-js", "index.js")
        main = os.path.join(raiz, "main.birl")

        env = os.environ.copy()
        env["BIRL_MODE"] = "gui"
        env["BIRL_GAME"] = jogo
        if extras:
            env.update({k: str(v) for k, v in extras.items()})

        self.proc = subprocess.Popen(
            [node, script, main],
            cwd=raiz,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            bufsize=0,
        )
        assert self.proc.stdout is not None
        assert self.proc.stderr is not None
        os.set_blocking(self.proc.stdout.fileno(), False)
        os.set_blocking(self.proc.stderr.fileno(), False)
        self._watches.append(
            GLib.io_add_watch(
                self.proc.stdout.fileno(),
                GLib.PRIORITY_DEFAULT,
                GLib.IO_IN | GLib.IO_HUP,
                self._ler_stdout,
            )
        )
        self._watches.append(
            GLib.io_add_watch(
                self.proc.stderr.fileno(),
                GLib.PRIORITY_DEFAULT,
                GLib.IO_IN | GLib.IO_HUP,
                self._ler_stderr,
            )
        )

    def _ler_stdout(self, fd: int, cond) -> bool:
        try:
            dados = os.read(fd, 65536)
        except BlockingIOError:
            return True
        except OSError:
            return False
        if not dados:
            codigo = self.proc.poll() if self.proc else 0
            self.emit("fim", codigo if codigo is not None else 0)
            return False
        self._buffer += dados
        while b"\n" in self._buffer:
            bruto, self._buffer = self._buffer.split(b"\n", 1)
            linha = bruto.decode("utf-8", "replace")
            self.emit("linha", linha)
        return True

    def _ler_stderr(self, fd: int, cond) -> bool:
        try:
            dados = os.read(fd, 65536)
        except (BlockingIOError, OSError):
            return True
        if not dados:
            return False
        self._erro_buffer += dados
        texto = self._erro_buffer.decode("utf-8", "replace")
        if texto.strip():
            self.emit("erro", texto)
            self._erro_buffer = b""
        return True

    def enviar(self, texto: str) -> None:
        if not self.proc or self.proc.poll() is not None:
            return
        assert self.proc.stdin is not None
        try:
            self.proc.stdin.write((texto + "\n").encode("utf-8"))
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError):
            pass

    def enviar_input(self, valor: str) -> None:
        self.enviar(f"INPUT {valor}")

    def parar(self) -> None:
        for watch in self._watches:
            try:
                GLib.source_remove(watch)
            except Exception:
                pass
        self._watches.clear()
        if not self.proc:
            return
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.proc = None
