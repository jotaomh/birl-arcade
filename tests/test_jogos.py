"""Testes de regressao do BIRL Arcade (python3 -m unittest discover -s tests)."""
import json
import random
import re
import shutil
import subprocess
import time
import unittest

from driver import NODE_BIRL, RAIZ, Partida, estrategia_dungeon

SAVE_PET = RAIZ / "saves" / "tamagotchi.json"


def rodar_terminal(entradas, **env_extra):
    import os
    env = dict(os.environ, **env_extra)
    env.pop("BIRL_MODE", None)
    r = subprocess.run(["node", NODE_BIRL, "main.birl"], cwd=RAIZ, input=entradas, env=env,
                       capture_output=True, text=True, timeout=60)
    return r.stdout, r.stderr


class TestNucleo(unittest.TestCase):
    def test_menu_sai_com_zero(self):
        saida, erro = rodar_terminal("0\n")
        self.assertIn("AGORA VAI COMER UM FRANGO", saida)
        self.assertEqual(erro, "")

    def test_enter_crlf_funciona(self):
        saida, erro = rodar_terminal("0\r\n")
        self.assertIn("AGORA VAI COMER UM FRANGO", saida)
        self.assertNotIn("ACABOU A ENTRADA", saida)

    def test_fim_da_entrada_nao_quebra(self):
        saida, erro = rodar_terminal("")
        self.assertIn("ACABOU A ENTRADA", saida)
        self.assertEqual(erro, "")

    def test_terminal_nao_vaza_protocolo_da_gui(self):
        saida, erro = rodar_terminal("5\n1\nq\n\n0\n")
        self.assertEqual(erro, "")
        for linha in saida.splitlines():
            self.assertFalse(linha.startswith(("SOM ", "DIALOGO ", "DATA ", "PROMPT ", "TEXT ")), linha)
        self.assertIn("VOCE SAIU DA DUNGEON", saida)

    def test_caixa_de_dialogo_no_terminal(self):
        saida, _ = rodar_terminal("5\n1\n")
        self.assertIn("| BAMBAM", saida)


class TestVelha(unittest.TestCase):
    @staticmethod
    def jogar(nivel, escolher):
        def estrategia(p, tipo, dica):
            if tipo == "cell":
                tab = p.estado.get("TABULEIRO", "." * 9).split()[0]
                return str(escolher([i for i, c in enumerate(tab) if c == "."]))
            return str(nivel) if tipo == "choice" else "ok"
        return Partida("velha").jogar(estrategia)

    def test_impossivel_nunca_perde(self):
        rnd = random.Random(42)
        for _ in range(6):
            p = self.jogar(3, rnd.choice)
            self.assertEqual(p.erros, [])
            self.assertIn(p.fim, ("BAMBAM", "EMPATE"), p.estado.get("TABULEIRO"))

    def test_facil_e_derrotavel(self):
        p = self.jogar(1, lambda livres: livres[0])
        self.assertEqual(p.fim, "VOCE")


class TestForca(unittest.TestCase):
    @staticmethod
    def jogar(*palavras):
        fila = iter(palavras)

        def estrategia(p, tipo, dica):
            if tipo == "text":
                return next(fila, None)
            return "ok"
        return Partida("forca").jogar(estrategia)

    def test_palavra_do_dicionario_o_bambam_ganha(self):
        for palavra in ("SUPINO", "WHEY", "ZEBRA"):
            p = self.jogar(palavra)
            self.assertEqual(p.erros, [], palavra)
            self.assertEqual(p.fim, "BAMBAM_GANHOU", palavra)
            self.assertLess(int(p.estado["ERROS"]), 6)
            self.assertEqual(p.estado["PADRAO"], palavra)

    def test_palavra_fora_do_dicionario_o_bambam_perde(self):
        p = self.jogar("ZZZZZ")
        self.assertEqual(p.fim, "BAMBAM_PERDEU")
        self.assertEqual(p.estado["ERROS"], "6")

    def test_valida_palavra_secreta(self):
        p = self.jogar("", "123", "A", "AÇÃO", "ab cd", "barra")
        self.assertEqual(p.erros, [])
        self.assertEqual(p.fim, "BAMBAM_GANHOU")
        self.assertEqual(sum(1 for l in p.linhas if l.startswith("PROMPT text")), 6)

    def test_letra_errada_elimina_palavras(self):
        p = self.jogar("SUPINO")
        chutes = [m.group(1) for l in p.linhas if (m := re.search(r"CHUTA (\w) \.\.\.", l))]
        self.assertEqual(len(chutes), len(set(chutes)), "chutou a mesma letra duas vezes")


class TestAcademia(unittest.TestCase):
    def jogar(self, sequencia, dias):
        contador = {"n": 0}

        def estrategia(p, tipo, dica):
            if tipo == "choice":
                contador["n"] += 1
                if contador["n"] > dias:
                    return "0"
                return sequencia[(contador["n"] - 1) % len(sequencia)]
            return "ok"
        return Partida("academia").jogar(estrategia)

    def test_numeros_inteiros_e_dentro_dos_limites(self):
        for sequencia in (["1"], ["1", "1", "4", "5"], ["2", "3", "4"], ["4"]):
            p = self.jogar(sequencia, 60)
            self.assertEqual(p.erros, [])
            self.assertEqual(p.suspeitas(), [])
            for linha in p.linhas:
                if linha.startswith("DATA ATRIBUTOS"):
                    a = {k: int(v) for k, v in (x.split("=") for x in linha.split()[2:] if x.split("=")[1].lstrip("-").isdigit())}
                    self.assertTrue(0 <= a["energia"] <= 100, linha)
                    self.assertTrue(0 <= a["fadiga"] <= 100, linha)
                    self.assertTrue(0 <= a["calorias"] <= 4000, linha)
                    self.assertTrue(0 <= a["proteina"] <= 300, linha)

    def test_comida_acaba_com_o_tempo(self):
        p = self.jogar(["5"], 8)
        ultimo = [l for l in p.linhas if l.startswith("DATA ATRIBUTOS")][-1]
        self.assertIn("calorias=0", ultimo)
        self.assertTrue(any("FOME" in l for l in p.linhas))


class TestTamagotchi(unittest.TestCase):
    def setUp(self):
        SAVE_PET.parent.mkdir(exist_ok=True)
        self.backup = SAVE_PET.read_text() if SAVE_PET.exists() else None
        SAVE_PET.unlink(missing_ok=True)

    def tearDown(self):
        if self.backup is None:
            SAVE_PET.unlink(missing_ok=True)
        else:
            SAVE_PET.write_text(self.backup)

    def salvar(self, **valores):
        base = {"treino": 60, "comida": 60, "vapo": 60, "hora": 2, "timestamp": int(time.time())}
        base.update(valores)
        SAVE_PET.write_text(json.dumps(base))

    def jogar(self, acoes, tempo="0"):
        fila = iter(acoes)
        return Partida("tamagotchi", tempo=tempo).jogar(lambda p, t, d: next(fila, "0") if t == "choice" else "ok")

    def test_novo_dia_depois_de_24_horas(self):
        self.salvar(hora=24)
        p = self.jogar(["2", "2", "2"])
        self.assertEqual(p.erros, [])
        self.assertTrue(any("NOVO DIA" in l for l in p.linhas))
        self.assertTrue(any("HORA...: 3 DE 24" in l for l in p.linhas))

    def test_save_corrompido_nao_quebra(self):
        SAVE_PET.write_text("{lixo")
        p = self.jogar([])
        self.assertEqual(p.erros, [])
        self.assertIn("treino=60", p.estado["PET"])

    def test_tempo_invalido_vira_zero(self):
        self.salvar()
        p = self.jogar([], tempo="abc")
        self.assertEqual(p.erros, [])
        self.assertIn("tempo=0", p.estado["PET"])

    def test_ausencia_gasta_energia_e_30h_mata(self):
        self.salvar(hora=2)
        p = self.jogar([], tempo="7200")
        self.assertIn("tempo=7200", p.estado["PET"])
        self.assertNotIn("treino=60", p.estado["PET"])
        p = self.jogar([], tempo="108000")
        self.assertTrue(any("MURCHOU" in l for l in p.linhas))

    def test_terminal_usa_o_mesmo_relogio_da_gui(self):
        self.salvar(timestamp=int(time.time()) - 7200)
        saida, erro = rodar_terminal("4\n0\n")
        self.assertEqual(erro, "")
        self.assertIn("PASSARAM 2 HORAS", saida)


class TestDungeon(unittest.TestCase):
    def jogar(self, personagem, semente):
        return Partida("dungeon", semente=semente).jogar(estrategia_dungeon(personagem))

    def test_bambam_zera_a_dungeon(self):
        p = self.jogar(1, 1)
        self.assertEqual((p.erros, p.fim), ([], "VITORIA"))

    def test_felipe_zera_a_dungeon(self):
        p = self.jogar(3, 1)
        self.assertEqual((p.erros, p.fim), ([], "VITORIA"))

    def test_toguro_joga_ate_o_fim(self):
        p = self.jogar(2, 7)
        self.assertEqual(p.erros, [])
        self.assertIn(p.fim, ("VITORIA", "DERROTA"))
        self.assertTrue(any("% DO PODER" in l for l in p.linhas))

    def test_mesma_semente_mesma_partida(self):
        a, b = self.jogar(1, 12345), self.jogar(1, 12345)
        self.assertEqual(a.linhas, b.linhas)
        c = self.jogar(1, 54321)
        self.assertNotEqual(a.linhas, c.linhas)

    def test_dados_d20_validos_e_sem_numeros_estranhos(self):
        p = self.jogar(1, 99)
        rolagens = [int(m.group(1)) for l in p.linhas if (m := re.search(r"D20: (\d+) \+", l))]
        self.assertGreater(len(rolagens), 5)
        self.assertTrue(all(1 <= r <= 20 for r in rolagens))
        self.assertGreater(len(set(rolagens)), 4)
        self.assertEqual(p.suspeitas(), [])

    def test_vida_nunca_passa_do_maximo(self):
        p = self.jogar(1, 5)
        for linha in p.linhas:
            if linha.startswith("DATA HEROI"):
                h = dict(x.split("=") for x in linha.split()[2:] if "=" in x)
                self.assertLessEqual(int(h["hp"]), int(h["hpmax"]), linha)
                self.assertGreaterEqual(int(h["hp"]), 0, linha)
                self.assertGreaterEqual(int(h["pump"]), 0, linha)

    def test_escolha_de_personagem_invalida_pergunta_de_novo(self):
        respostas = iter(["9", "x", "2"])

        def estrategia(p, tipo, dica):
            return next(respostas, "q") if tipo == "choice" else ("q" if tipo == "move" else "ok")
        p = Partida("dungeon", semente=1).jogar(estrategia)
        self.assertEqual(p.erros, [])
        self.assertEqual(p.fim, "SAIU")
        self.assertIn("TOGURO", p.estado["HEROI"])


if __name__ == "__main__":
    unittest.main()
