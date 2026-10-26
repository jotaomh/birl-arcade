#!/usr/bin/env python3
"""BIRL Arcade - interface grafica GTK4 (casca fina sobre o cerebro BIRL)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, GLib, Gtk, Pango  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from protocolo import MotorBirl  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SALVE_PET = RAIZ / "saves" / "tamagotchi.json"

JOGOS = [
    ("velha", "Jogo da Velha", "Bambam com minimax e niveis de dificuldade"),
    ("forca", "Forca", "O Bambam adivinha a palavra que voce escolher"),
    ("academia", "Simulador de Academia", "Fadiga, dieta, sobrecarga e lesao por regra"),
    ("tamagotchi", "Tamagotchi do Monstro", "O estado evolui pelo tempo real"),
    ("dungeon", "Dungeon da Academia", "Fases desenhadas a mao e inimigos com BFS"),
]

CSS = """
window { background: #14161a; }
.titulo { font-size: 30px; font-weight: 800; color: #ffcc33; }
.subtitulo { color: #aab2bd; }
.menu-card { background: #1e2229; border-radius: 10px; padding: 18px; }
.menu-card:hover { background: #262b34; }
.menu-nome { font-size: 19px; font-weight: 700; color: #f2f4f7; }
.menu-desc { color: #9aa3ae; font-size: 12px; }
.painel { background: #1b1f26; border-radius: 10px; padding: 14px; }
.log { background: #0d0f12; color: #d7dde5; font-family: monospace; font-size: 13px; padding: 10px; }
.stat { color: #dfe6ee; font-family: monospace; }
.destaque { color: #ffcc33; font-weight: 700; }
.erro { color: #ff6b6b; font-family: monospace; }
.casa { font-size: 26px; font-weight: 800; min-width: 58px; min-height: 58px; }
.parede { background: #2b3038; color: #2b3038; }
.chao { color: #55606d; }
.heroi { color: #ffcc33; font-weight: 800; }
.inimigo { color: #ff6b6b; font-weight: 800; }
.item { color: #6ee7a8; font-weight: 800; }
.saida { color: #7dd3fc; font-weight: 800; }
button.acao { padding: 8px 10px; }
.dialogo { background: #1e2229; border: 3px solid #ffcc33; border-radius: 10px; padding: 12px; }
.dialogo-nome { font-size: 16px; font-weight: 800; color: #ffcc33; }
.dialogo-texto { font-size: 14px; color: #d7dde5; font-family: monospace; }
.dialogo-retrato { min-width: 64px; min-height: 64px; border: 2px solid #f5c542; border-radius: 4px; color: #f5c542; font-size: 40px; font-weight: bold; }
"""


def carregar_save_pet() -> tuple[dict | None, int]:
    if not SALVE_PET.exists():
        return None, 0
    try:
        dados = json.loads(SALVE_PET.read_text(encoding="utf-8"))
        agora = int(GLib.get_real_time() / 1_000_000)
        passado = int(dados.get("timestamp", agora))
        return dados, max(0, agora - passado)
    except Exception:
        return None, 0


def gravar_save_pet(campos: dict[str, str]) -> None:
    try:
        SALVE_PET.parent.mkdir(parents=True, exist_ok=True)
        agora = int(GLib.get_real_time() / 1_000_000)
        dados = {
            "treino": int(float(campos.get("treino", 0))),
            "comida": int(float(campos.get("comida", 0))),
            "vapo": int(float(campos.get("vapo", 0))),
            "hora": int(float(campos.get("hora", 0))),
            "timestamp": agora,
        }
        SALVE_PET.write_text(json.dumps(dados), encoding="utf-8")
    except Exception as exc:
        print(f"nao consegui salvar o pet: {exc}", file=sys.stderr)


class ArcadeApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.birl.arcade")
        self.janela: Gtk.ApplicationWindow | None = None
        self.stack: Gtk.Stack | None = None
        self.pagina_jogo: GamePage | None = None

    def do_activate(self) -> None:
        if self.janela is None:
            self.janela = Gtk.ApplicationWindow(application=self)
            self.janela.set_title("BIRL Arcade")
            self.janela.set_default_size(1100, 760)
            self.janela.connect("close-request", self._ao_fechar)

            provedor = Gtk.CssProvider()
            provedor.load_from_data(CSS.encode("utf-8"))
            display = Gdk.Display.get_default()
            if display is not None:
                Gtk.StyleContext.add_provider_for_display(
                    display, provedor, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

            self.stack = Gtk.Stack()
            self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
            self.janela.set_child(self.stack)
            self.stack.add_named(self._montar_menu(), "menu")
            self.stack.set_visible_child_name("menu")

        self.janela.present()

    def _montar_menu(self) -> Gtk.Widget:
        caixa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        caixa.set_margin_top(42)
        caixa.set_margin_bottom(42)
        caixa.set_margin_start(64)
        caixa.set_margin_end(64)

        titulo = Gtk.Label(label="B I R L   A R C A D E")
        titulo.add_css_class("titulo")
        caixa.append(titulo)

        sub = Gtk.Label(label="Aqui nao tem agua com musculo. O cerebro e BIRL; a janela e so o espelho.")
        sub.add_css_class("subtitulo")
        caixa.append(sub)

        grade = Gtk.Grid()
        grade.set_row_spacing(12)
        grade.set_column_spacing(12)
        grade.set_margin_top(18)
        grade.set_hexpand(True)
        grade.set_vexpand(True)

        for indice, (chave, nome, desc) in enumerate(JOGOS):
            botao = Gtk.Button()
            botao.add_css_class("menu-card")
            botao.set_hexpand(True)
            botao.set_vexpand(True)
            conteudo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            rotulo = Gtk.Label(label=nome, xalign=0)
            rotulo.add_css_class("menu-nome")
            detalhe = Gtk.Label(label=desc, xalign=0)
            detalhe.add_css_class("menu-desc")
            detalhe.set_wrap(True)
            conteudo.append(rotulo)
            conteudo.append(detalhe)
            botao.set_child(conteudo)
            botao.connect("clicked", lambda _b, c=chave: self.abrir_jogo(c))
            grade.attach(botao, indice % 2, indice // 2, 1, 1)

        caixa.append(grade)

        sair = Gtk.Button(label="Sair do fliperama")
        sair.connect("clicked", lambda _b: self.quit())
        caixa.append(sair)
        return caixa

    def abrir_jogo(self, chave: str) -> None:
        if self.pagina_jogo is not None:
            self.pagina_jogo.encerrar()
        self.pagina_jogo = GamePage(self, chave)
        self.stack.add_named(self.pagina_jogo, f"jogo-{chave}")
        self.stack.set_visible_child_name(f"jogo-{chave}")
        self.pagina_jogo.iniciar()

    def voltar_menu(self) -> None:
        if self.pagina_jogo is not None:
            self.pagina_jogo.encerrar()
            self.pagina_jogo = None
        self.stack.set_visible_child_name("menu")

    def _ao_fechar(self, *_args) -> bool:
        if self.pagina_jogo is not None:
            self.pagina_jogo.encerrar()
        return False


class GamePage(Gtk.Box):
    def __init__(self, app: ArcadeApp, chave: str):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.app = app
        self.chave = chave
        self.titulo = next((n for c, n, _d in JOGOS if c == chave), chave)
        self.motor: MotorBirl | None = None
        self.dados: dict[str, str] = {}
        self.prompt_atual: tuple[str, str] | None = None
        self.encerrado = False
        self._buffer_prompt = ""
        # Dialogo (Undertale/Pokemon style)
        self.dialogo_ativo = False
        self.dialogo_personagem = ""
        self.dialogo_texto_completo = ""
        self.dialogo_texto_atual = ""
        self.dialogo_indice = 0
        self.dialogo_timer = None
        self.dialogo_velocidade = 30  # ms por letra
        self.dialogo_widget = None
        self.dialogo_nome_label = None
        self.dialogo_texto_label = None
        self.dialogo_retrato = None
        self.dialogo_imagem = None
        # Audio
        self.volume = 0.7
        self.mutado = False
        self.audio_dir = RAIZ / "assets" / "audio"
        self.manifest = self._carregar_manifest()

        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)

        cab = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        voltar = Gtk.Button(label="< Menu")
        voltar.connect("clicked", lambda _b: self.app.voltar_menu())
        cab.append(voltar)
        nome = Gtk.Label(label=self.titulo, xalign=0)
        nome.add_css_class("destaque")
        nome.set_hexpand(True)
        cab.append(nome)
        self.append(cab)

        conteudo = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        conteudo.set_vexpand(True)

        rolagem = Gtk.ScrolledWindow()
        rolagem.set_hexpand(True)
        rolagem.set_vexpand(True)
        self.log = Gtk.TextView()
        self.log.set_editable(False)
        self.log.set_cursor_visible(False)
        self.log.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.log.add_css_class("log")
        self.log_buffer = self.log.get_buffer()
        rolagem.set_child(self.log)
        conteudo.append(rolagem)

        lado = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        lado.set_size_request(350, -1)
        self.painel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.painel.add_css_class("painel")
        self.painel.set_valign(Gtk.Align.START)
        lado.append(self.painel)

        self.acoes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.acoes.set_valign(Gtk.Align.START)
        lado.append(self.acoes)

        self.entrada = Gtk.Entry()
        self.entrada.set_placeholder_text("Digite e aperte Enter")
        self.entrada.connect("activate", self._ao_enviar_entrada)
        self.entrada.set_visible(False)
        lado.append(self.entrada)

        # Caixa de dialogo (Undertale/Pokemon style) - inicialmente escondida
        self.dialogo_widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.dialogo_widget.add_css_class("dialogo")
        self.dialogo_widget.set_hexpand(True)
        self.dialogo_widget.set_vexpand(False)
        self.dialogo_widget.set_visible(False)

        self.dialogo_retrato = Gtk.Label(label="?")
        self.dialogo_retrato.add_css_class("dialogo-retrato")
        self.dialogo_retrato.set_halign(Gtk.Align.START)
        self.dialogo_retrato.set_valign(Gtk.Align.START)
        self.dialogo_retrato.set_size_request(96, 96)
        self.dialogo_widget.append(self.dialogo_retrato)

        self.dialogo_imagem = Gtk.Picture()
        self.dialogo_imagem.set_size_request(96, 96)
        self.dialogo_imagem.set_content_fit(Gtk.ContentFit.CONTAIN)
        self.dialogo_imagem.set_halign(Gtk.Align.START)
        self.dialogo_imagem.set_valign(Gtk.Align.START)
        self.dialogo_imagem.set_visible(False)
        self.dialogo_widget.append(self.dialogo_imagem)

        texto_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        texto_box.set_hexpand(True)
        self.dialogo_nome_label = Gtk.Label(label="")
        self.dialogo_nome_label.add_css_class("dialogo-nome")
        self.dialogo_nome_label.set_xalign(0)
        texto_box.append(self.dialogo_nome_label)
        self.dialogo_texto_label = Gtk.Label(label="")
        self.dialogo_texto_label.add_css_class("dialogo-texto")
        self.dialogo_texto_label.set_xalign(0)
        self.dialogo_texto_label.set_halign(Gtk.Align.START)
        texto_box.append(self.dialogo_texto_label)
        self.dialogo_widget.append(texto_box)

        dica = Gtk.Label(label="(Z ou Enter para avancar)")
        dica.add_css_class("stat")
        dica.set_xalign(1)
        dica.set_hexpand(True)
        texto_box.append(dica)

        self.botao_voltar = Gtk.Button(label="Voltar ao menu")
        self.botao_voltar.set_visible(False)
        self.botao_voltar.connect("clicked", lambda _b: self.app.voltar_menu())
        lado.append(self.botao_voltar)

        conteudo.append(lado)
        self.append(conteudo)
        # caixa de dialogo na parte de baixo da tela (estilo Undertale / Pokemon)
        self.append(self.dialogo_widget)

        controlador = Gtk.EventControllerKey()
        controlador.connect("key-pressed", self._ao_tecla)
        self.add_controller(controlador)

    def iniciar(self) -> None:
        extras: dict[str, str] = {}
        if self.chave == "tamagotchi":
            _dados, decorrido = carregar_save_pet()
            extras["BIRL_TEMPO"] = str(decorrido)
        self._log("Carregando o cerebro BIRL...")
        self.motor = MotorBirl(str(RAIZ), self.chave, extras)
        self.motor.connect("linha", self._ao_linha)
        self.motor.connect("erro", self._ao_erro)
        self.motor.connect("fim", self._ao_fim)

    def encerrar(self) -> None:
        self.encerrado = True
        if self.motor is not None:
            self.motor.parar()
            self.motor = None

    def _log(self, texto: str) -> None:
        final = self.log_buffer.get_end_iter()
        self.log_buffer.insert(final, texto + "\n")
        marca = self.log_buffer.create_mark(None, self.log_buffer.get_end_iter(), False)
        self.log.scroll_mark_onscreen(marca)

    def _ao_linha(self, _motor, linha: str) -> None:
        if linha.startswith("TEXT "):
            self._log(linha[5:])
        elif linha == "TEXT":
            self._log("")
        elif linha.startswith("DATA "):
            self._ao_dado(linha[5:])
        elif linha.startswith("PROMPT "):
            resto = linha[7:]
            tipo, _, dica = resto.partition(" ")
            self._ao_prompt(tipo, dica)
        elif linha.startswith("END "):
            self._ao_fim_jogo(linha[4:])
        elif linha.startswith("END"):
            self._ao_fim_jogo("")
        elif linha.startswith("DIALOGO "):
            resto = linha[8:]
            personagem, _, texto = resto.partition("|")
            self._iniciar_dialogo(personagem, texto)
        elif linha.startswith("SOM "):
            som_id = linha[4:].strip()
            self._tocar_som(som_id)

    def _ao_dado(self, bruto: str) -> None:
        chave, _, valor = bruto.partition(" ")
        self.dados[chave] = valor
        if chave == "SAVE":
            campos: dict[str, str] = {}
            for par in valor.split():
                k, _, v = par.partition("=")
                campos[k] = v
            gravar_save_pet(campos)
        self._renderizar()

    def _ao_prompt(self, tipo: str, dica: str) -> None:
        self.prompt_atual = (tipo, dica)
        self._renderizar()

    def _ao_fim_jogo(self, resultado: str) -> None:
        if self.encerrado:
            return
        self.encerrado = True
        texto = self._texto_resultado(resultado)
        self._log("")
        self._log(f"== {texto} ==")
        self._limpar_acoes()
        self.entrada.set_visible(False)
        self.botao_voltar.set_visible(True)

    def _texto_resultado(self, resultado: str) -> str:
        mapa = {
            "VOCE": "Voce amassolou o Bambam!",
            "BAMBAM": "O Bambam te amassolou.",
            "EMPATE": "Empate. Ninguem murchou.",
            "BAMBAM_GANHOU": "O Bambam adivinhou a palavra!",
            "BAMBAM_PERDEU": "O Bambam nao adivinhou. Voce venceu!",
            "VITORIA": "Vitoria! BIRL!",
            "DERROTA": "Derrota. Volta pro supino, frango.",
            "MURCHOU": "Seu monstro murchou...",
            "SAIU": "Voce saiu do jogo.",
            "EM_BREVE": "Jogo em construcao.",
            "EOF": "O cerebro BIRL encerrou.",
        }
        return mapa.get(resultado, resultado or "Fim de jogo")

    def _ao_erro(self, _motor, texto: str) -> None:
        self._log("ERRO BIRL: " + texto.strip())

    def _ao_fim(self, _motor, codigo: int) -> None:
        if not self.encerrado and self.motor is not None:
            self._log(f"Processo BIRL terminou (codigo {codigo}).")

    def _limpar_acoes(self) -> None:
        while True:
            filho = self.acoes.get_first_child()
            if filho is None:
                break
            self.acoes.remove(filho)
        self.entrada.set_visible(False)

    def _botao_acao(self, rotulo: str, valor: str) -> Gtk.Button:
        botao = Gtk.Button(label=rotulo)
        botao.add_css_class("acao")
        botao.connect("clicked", lambda _b, v=valor: self._enviar(v))
        self.acoes.append(botao)
        return botao

    def _iniciar_dialogo(self, personagem: str, texto: str) -> None:
        if self.dialogo_timer is not None:
            GLib.source_remove(self.dialogo_timer)
            self.dialogo_timer = None
        self.dialogo_ativo = True
        self.dialogo_personagem = personagem
        self.dialogo_texto_completo = texto
        self.dialogo_texto_atual = ""
        self.dialogo_indice = 0
        self.dialogo_widget.set_visible(True)
        self.dialogo_nome_label.set_label(personagem)
        retrato_id = self.dados.get("RETRATO", "").strip() or self._normalizar_id(personagem)
        caminho = RAIZ / "assets" / "portraits" / f"{retrato_id}.png"
        if caminho.exists():
            try:
                self.dialogo_imagem.set_filename(str(caminho))
                self.dialogo_imagem.set_visible(True)
                self.dialogo_retrato.set_visible(False)
            except Exception:
                self.dialogo_imagem.set_visible(False)
                self.dialogo_retrato.set_visible(True)
                self.dialogo_retrato.set_label(personagem[:1].upper() or "?")
        else:
            self.dialogo_imagem.set_visible(False)
            self.dialogo_retrato.set_visible(True)
            self.dialogo_retrato.set_label(personagem[:1].upper() or "?")
        self._digitar_letra()

    @staticmethod
    def _normalizar_id(nome: str) -> str:
        import re
        import unicodedata

        base = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^a-z0-9]+", "_", base.lower()).strip("_")

    def _digitar_letra(self) -> None:
        if not self.dialogo_ativo:
            return
        if self.dialogo_indice < len(self.dialogo_texto_completo):
            self.dialogo_texto_atual = self.dialogo_texto_completo[: self.dialogo_indice + 1]
            self.dialogo_texto_label.set_label(self.dialogo_texto_atual)
            self.dialogo_indice += 1
            self.dialogo_timer = GLib.timeout_add(
                self.dialogo_velocidade, self._digitar_letra
            )
        else:
            self.dialogo_timer = None

    def _avancar_dialogo(self) -> None:
        if not self.dialogo_ativo:
            return
        if self.dialogo_timer is not None:
            GLib.source_remove(self.dialogo_timer)
            self.dialogo_timer = None
            self.dialogo_texto_atual = self.dialogo_texto_completo
            self.dialogo_texto_label.set_label(self.dialogo_texto_atual)
            self.dialogo_indice = len(self.dialogo_texto_completo)
        else:
            self.dialogo_ativo = False
            self.dialogo_widget.set_visible(False)
            self.dialogo_texto_atual = ""
            self.dialogo_texto_label.set_label("")

    def _carregar_manifest(self) -> dict[str, str]:
        manifest: dict[str, str] = {}
        caminho = self.audio_dir / "manifest.txt"
        if not caminho.exists():
            return manifest
        try:
            for linha in caminho.read_text(encoding="utf-8").splitlines():
                linha = linha.strip()
                if not linha or linha.startswith("#"):
                    continue
                partes = linha.split("=", 1)
                if len(partes) == 2:
                    manifest[partes[0].strip()] = partes[1].strip()
        except Exception:
            pass
        return manifest

    def _tocar_som(self, som_id: str) -> None:
        if self.mutado:
            return
        arquivo = self.manifest.get(som_id, som_id + ".wav")
        caminho = self.audio_dir / arquivo
        if not caminho.exists():
            return
        try:
            import subprocess
            # Toca em segundo plano, nao trava o jogo
            subprocess.Popen(
                ["paplay", str(caminho)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            try:
                import subprocess
                subprocess.Popen(
                    ["aplay", str(caminho)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass

    def _ao_tecla(self, _ctrl, tecla, _codigo, _mods) -> bool:
        if self.encerrado:
            return False
        if tecla == Gdk.KEY_m:
            self.mutado = not self.mutado
            estado = "MUTO" if self.mutado else "SOM LIGADO"
            self._log(f"Audio: {estado}")
            return True
        if self.dialogo_ativo and tecla in (
            Gdk.KEY_z, Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space
        ):
            self._avancar_dialogo()
            return True
        if self.entrada.get_visible() and self.entrada.has_focus():
            return False
        if self.prompt_atual and self.prompt_atual[0] == "move":
            mapa = {
                Gdk.KEY_w: "w", Gdk.KEY_a: "a", Gdk.KEY_s: "s", Gdk.KEY_d: "d", Gdk.KEY_q: "q",
                Gdk.KEY_W: "w", Gdk.KEY_A: "a", Gdk.KEY_S: "s", Gdk.KEY_D: "d", Gdk.KEY_Q: "q",
                Gdk.KEY_Up: "w", Gdk.KEY_Left: "a", Gdk.KEY_Down: "s", Gdk.KEY_Right: "d",
            }
            if tecla in mapa:
                self._enviar(mapa[tecla])
                return True
        if self.prompt_atual and self.prompt_atual[0] == "choice":
            nome = Gdk.keyval_name(tecla) or ""
            if len(nome) == 1 and nome.isdigit():
                valores = [i.partition("=")[0] for i in self.dados.get("OPCOES", "").split("|") if i]
                if nome in valores:
                    self._enviar(nome)
                    return True
        return False

    def _ao_enviar_entrada(self, _entry) -> None:
        texto = self.entrada.get_text().strip()
        if not texto:
            return
        self.entrada.set_text("")
        self._enviar(texto)

    def _enviar(self, valor: str) -> None:
        if self.motor is None or self.encerrado:
            return
        self._limpar_acoes()
        self.motor.enviar_input(valor)

    def _renderizar(self) -> None:
        self._limpar_acoes()
        self._renderizar_painel()
        if self.prompt_atual is None:
            return
        tipo, dica = self.prompt_atual
        rotulo = Gtk.Label(label=dica, xalign=0)
        rotulo.set_wrap(True)
        rotulo.add_css_class("stat")
        self.acoes.append(rotulo)

        if tipo == "next":
            self._botao_acao("Continuar", "ok")
        elif tipo == "choice":
            opcoes = self.dados.get("OPCOES", "")
            for item in opcoes.split("|"):
                if not item:
                    continue
                valor, _, nome = item.partition("=")
                self._botao_acao(nome or valor, valor)
        elif tipo == "cell":
            self._renderizar_velha()
        elif tipo == "move":
            self._renderizar_movimento()
        else:
            self.entrada.set_visible(True)
            self.entrada.grab_focus()

    def _renderizar_painel(self) -> None:
        while True:
            filho = self.painel.get_first_child()
            if filho is None:
                break
            self.painel.remove(filho)

        if self.chave == "velha":
            self._painel_velha()
        elif self.chave == "forca":
            self._painel_forca()
        elif self.chave == "academia":
            self._painel_academia()
        elif self.chave == "tamagotchi":
            self._painel_pet()
        elif self.chave == "dungeon":
            self._painel_dungeon()
        else:
            for chave, valor in self.dados.items():
                self.painel.append(Gtk.Label(label=f"{chave}: {valor}", xalign=0))

    def _linha_stat(self, texto: str, classe: str = "stat") -> None:
        rotulo = Gtk.Label(label=texto, xalign=0)
        rotulo.add_css_class(classe)
        self.painel.append(rotulo)

    def _barra(self, nome: str, valor: int, maximo: int = 100) -> None:
        linha = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        rotulo = Gtk.Label(label=f"{nome}: {valor}", xalign=0)
        rotulo.add_css_class("stat")
        linha.append(rotulo)
        barra = Gtk.ProgressBar()
        barra.set_fraction(max(0.0, min(1.0, valor / maximo if maximo else 0)))
        linha.append(barra)
        self.painel.append(linha)

    def _campos(self, chave: str) -> dict[str, str]:
        campos: dict[str, str] = {}
        for par in self.dados.get(chave, "").split():
            k, _, v = par.partition("=")
            campos[k] = v
        return campos

    def _painel_velha(self) -> None:
        self._linha_stat("Jogo da Velha", "destaque")
        vez = self.dados.get("VEZ", "?")
        self._linha_stat(f"Vez: {vez}")
        nivel = self.dados.get("NIVEL", "")
        if nivel:
            self._linha_stat(f"Dificuldade: {nivel}")

    def _renderizar_velha(self) -> None:
        tab = self.dados.get("TABULEIRO", ".........")
        grade = Gtk.Grid()
        grade.set_row_spacing(6)
        grade.set_column_spacing(6)
        for pos in range(9):
            simbolo = tab[pos] if pos < len(tab) else "."
            texto = " " if simbolo == "." else simbolo
            botao = Gtk.Button(label=texto)
            botao.add_css_class("casa")
            botao.set_sensitive(simbolo == ".")
            botao.connect("clicked", lambda _b, p=pos: self._enviar(str(p)))
            grade.attach(botao, pos % 3, pos // 3, 1, 1)
        self.acoes.append(grade)

    def _painel_forca(self) -> None:
        self._linha_stat("Forca do Bambam", "destaque")
        self._linha_stat(f"Palavra: {self.dados.get('PADRAO', '')}")
        self._linha_stat(f"Certas: {self.dados.get('CERTAS', '-')}")
        self._linha_stat(f"Erradas: {self.dados.get('ERRADAS', '-')}")
        self._linha_stat(f"Tentativas: {self.dados.get('ERROS', '0')} / {self.dados.get('MAX', '6')}")
        if self.dados.get("DICA"):
            self._linha_stat(self.dados["DICA"])

    def _painel_academia(self) -> None:
        c = self._campos("ATRIBUTOS")
        self._linha_stat("Ficha do Monstro", "destaque")
        for nome in ("forca", "shape", "energia", "fadiga", "lesao", "dia", "meta"):
            if nome in c:
                self._linha_stat(f"{nome.upper()}: {c[nome]}")
        for nome in ("calorias", "proteina"):
            if nome in c:
                self._linha_stat(f"{nome.upper()}: {c[nome]}")

    def _painel_pet(self) -> None:
        c = self._campos("PET")
        self._linha_stat("Seu Monstro", "destaque")
        for nome in ("treino", "comida", "vapo"):
            if nome in c:
                try:
                    self._barra(nome.upper(), int(float(c[nome])))
                except ValueError:
                    pass
        self._linha_stat(f"Hora: {c.get('hora', '0')} / 24")
        if c.get("tempo"):
            self._linha_stat(f"Tempo real decorrido: {c['tempo']}s")

    def _painel_dungeon(self) -> None:
        c = self._campos("HEROI")
        self._linha_stat("Dungeon da Academia", "destaque")
        if c.get("nome"):
            self._linha_stat(f"{c['nome']}  NIVEL {c.get('nivel', '1')}  (XP {c.get('xp', '0')})")
        try:
            self._barra(f"VIDA (max {c.get('hpmax', '?')})",
                        int(float(c.get("hp", 0))), int(float(c.get("hpmax", 1)) or 1))
            self._barra(f"PUMP (max {c.get('pumpmax', '?')})",
                        int(float(c.get("pump", 0))), int(float(c.get("pumpmax", 1)) or 1))
        except ValueError:
            pass
        self._linha_stat(f"ATAQUE: {c.get('atk', '?')}  DEFESA: {c.get('def', '?')}  WHEY: {c.get('itens', '0')}")
        self._linha_stat(f"FASE: {c.get('fase', '?')} / 3")
        inim = self._campos("INIM")
        try:
            hpmax_inim = int(float(inim.get("hpmax", 0)))
        except ValueError:
            hpmax_inim = 0
        if hpmax_inim > 0:
            self._linha_stat(f"INIMIGO: {self.dados.get('INIM', '').split(' hp=')[0].replace('nome=', '')}", "erro")
            self._barra(f"HP DO INIMIGO (max {inim.get('hpmax', '?')})",
                        max(0, int(float(inim.get("hp", 0)))), hpmax_inim)
        mapa = self.dados.get("MAPA", "")
        if len(mapa) >= 100:
            grade = Gtk.Grid()
            grade.set_row_spacing(0)
            grade.set_column_spacing(0)
            for pos, simbolo in enumerate(mapa[:100]):
                classe = {"#": "parede", ".": "chao", "@": "heroi", "F": "inimigo",
                          "P": "inimigo", "W": "item", "C": "item", "E": "saida"}.get(simbolo, "chao")
                rotulo = Gtk.Label(label=simbolo)
                rotulo.add_css_class(classe)
                rotulo.set_size_request(18, 18)
                grade.attach(rotulo, pos % 10, pos // 10, 1, 1)
            self.painel.append(grade)

    def _renderizar_movimento(self) -> None:
        grade = Gtk.Grid()
        grade.set_row_spacing(4)
        grade.set_column_spacing(4)
        botoes = [("", 0, 0), ("W", 1, 0), ("", 2, 0),
                  ("A", 0, 1), ("S", 1, 1), ("D", 2, 1)]
        for rotulo, x, y in botoes:
            if not rotulo:
                continue
            botao = Gtk.Button(label=rotulo)
            botao.connect("clicked", lambda _b, v=rotulo.lower(): self._enviar(v))
            grade.attach(botao, x, y, 1, 1)
        self.acoes.append(grade)
        self._botao_acao("Sair da dungeon (Q)", "q")


def main() -> int:
    app = ArcadeApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
