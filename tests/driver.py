"""Joga o BIRL Arcade pelo mesmo protocolo de texto que a interface grafica usa."""
import collections
import os
import queue
import re
import subprocess
import threading
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
NODE_BIRL = str(RAIZ / "node_modules" / "birl-js" / "index.js")


class Partida:
    def __init__(self, jogo, tempo="0", semente=None, modo="gui", timeout=90):
        env = dict(os.environ, BIRL_MODE=modo, BIRL_GAME=jogo, BIRL_TEMPO=str(tempo))
        env.pop("BIRL_SEED", None)
        if semente is not None:
            env["BIRL_SEED"] = str(semente)
        self.p = subprocess.Popen(
            ["node", NODE_BIRL, "main.birl"], cwd=RAIZ, env=env, text=True, bufsize=1,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.q = queue.Queue()
        self.erros = []
        self.linhas = []
        self.estado = {}
        self.fim = None
        self.timeout = timeout
        for fluxo, nome in ((self.p.stdout, "out"), (self.p.stderr, "err")):
            threading.Thread(target=self._ler, args=(fluxo, nome), daemon=True).start()

    def _ler(self, fluxo, nome):
        for linha in fluxo:
            self.q.put((nome, linha.rstrip("\n")))
        self.q.put((nome, None))

    def enviar(self, texto):
        try:
            self.p.stdin.write("INPUT " + texto + "\n")
            self.p.stdin.flush()
        except OSError:
            pass

    def jogar(self, estrategia, max_prompts=1500):
        inicio, prompts, fechados = time.time(), 0, 0
        while fechados < 2:
            try:
                nome, linha = self.q.get(timeout=15)
            except queue.Empty:
                self.erros.append("TRAVOU: sem saida por 15s")
                break
            if linha is None:
                fechados += 1
                continue
            if nome == "err":
                self.erros.append("STDERR: " + linha)
                continue
            self.linhas.append(linha)
            if linha.startswith("DATA "):
                chave, _, valor = linha[5:].partition(" ")
                self.estado[chave] = valor
            elif linha.startswith("END "):
                self.fim = linha[4:]
            elif linha.startswith("PROMPT "):
                prompts += 1
                if prompts > max_prompts or time.time() - inicio > self.timeout:
                    self.erros.append("PROMPTS/TEMPO DEMAIS (laco infinito?)")
                    break
                _, tipo, dica = (linha.split(" ", 2) + ["", ""])[:3]
                resposta = estrategia(self, tipo, dica)
                if resposta is None:
                    break
                self.enviar(resposta)
        try:
            self.p.stdin.close()
        except OSError:
            pass
        try:
            self.p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.p.kill()
            self.p.wait()
            self.erros.append("processo nao encerrou sozinho")
        for fluxo in (self.p.stdout, self.p.stderr):
            try:
                fluxo.close()
            except OSError:
                pass
        return self

    def campos(self, chave):
        return dict(p.partition("=")[::2] for p in self.estado.get(chave, "").split() if "=" in p)

    def opcoes(self):
        return [i.partition("=")[0] for i in self.estado.get("OPCOES", "").split("|") if i]

    def suspeitas(self):
        ruim = re.compile(r"NaN|undefined|\[object|Infinity|\bnull\b|\d\.\d{3,}")
        return [l for l in self.linhas if ruim.search(l)]


def bfs(mapa, objetivos):
    inicio = mapa.index("@")
    fila, vistos = collections.deque([(inicio, "")]), {inicio}
    while fila:
        pos, caminho = fila.popleft()
        x, y = pos % 10, pos // 10
        for tecla, (dx, dy) in {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < 10 and 0 <= ny < 10):
                continue
            nova = ny * 10 + nx
            if nova in vistos or mapa[nova] == "#":
                continue
            if mapa[nova] in objetivos:
                return caminho + tecla
            if mapa[nova] in "FE":
                continue
            vistos.add(nova)
            fila.append((nova, caminho + tecla))
    return None


def estrategia_dungeon(personagem):
    memoria = {}

    def estrategia(p, tipo, dica):
        h = p.campos("HEROI")
        hp, hpmax, pump, itens = (int(h.get(k, 0)) for k in ("hp", "hpmax", "pump", "itens"))
        opcoes = p.estado.get("OPCOES", "")
        chaves = p.opcoes()
        if tipo == "move":
            mapa = p.estado.get("MAPA", "")
            for alvo in ("WC" if hp < hpmax * 0.7 else "W", "F", "E"):
                if alvo == "E" and "F" in mapa:
                    continue
                caminho = bfs(mapa, alvo)
                if caminho:
                    return caminho[0]
            return "q"
        if tipo == "choice":
            if "BAMBAM" in opcoes and "TOGURO" in opcoes:
                return str(personagem)
            if "PODER" in dica:
                return next((k for k in ("100", "80", "50", "20") if k in chaves), "20")
            if "VOLTAR" in opcoes:
                quer = memoria.get("quer", "0")
                return quer if quer in chaves else "0"
            if "ATACAR" in opcoes:
                baixo = hp < hpmax * 0.45
                memoria["quer"] = "0"
                if baixo and itens > 0:
                    return "3"
                if personagem == 1:
                    if baixo and pump >= 5:
                        memoria["quer"] = "2"
                        return "2"
                    if pump >= 10:
                        memoria["quer"] = "1"
                        return "2"
                if personagem == 2 and pump >= 10:
                    memoria["quer"] = "1"
                    return "2"
                if personagem == 3:
                    if hp < hpmax * 0.55 and pump >= 5:
                        memoria["quer"] = "2"
                        return "2"
                    if hp < hpmax * 0.8 and pump >= 8:
                        memoria["quer"] = "4"
                        return "2"
                    if pump >= 10 and not memoria.get("ficha"):
                        memoria["quer"] = "5"
                        memoria["ficha"] = True
                        return "2"
                return "1"
            return chaves[0] if chaves else "1"
        return "ok"

    return estrategia
