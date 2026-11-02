"""Ditado BR: segure uma tecla, fale e o texto aparece onde o cursor estiver."""

import ctypes
import datetime
import os
import queue
import sys
import threading
import tkinter as tk

import pystray
from PIL import Image, ImageDraw
from pynput import keyboard

from . import atalhos, audio, colar, config
from .janela import Pilula
from .transcrever import Transcritor

NOMES_TECLAS = {
    "ctrl_r": "Ctrl direito", "alt_r": "Alt direito (AltGr)", "f8": "F8", "f9": "F9",
    "caps_lock": "Caps Lock", "scroll_lock": "Scroll Lock", "pause": "Pause",
}


def icone(cor=(255, 122, 69)) -> Image.Image:
    e = 4
    img = Image.new("RGBA", (64 * e, 64 * e), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([4 * e, 4 * e, 60 * e, 60 * e], radius=16 * e, fill=(20, 20, 22, 255))
    d.rounded_rectangle([24 * e, 13 * e, 40 * e, 38 * e], radius=8 * e, fill=cor)          # microfone
    d.arc([17 * e, 22 * e, 47 * e, 46 * e], 0, 180, fill=cor, width=3 * e)
    d.line([32 * e, 46 * e, 32 * e, 52 * e], fill=cor, width=3 * e)
    d.line([25 * e, 52 * e, 39 * e, 52 * e], fill=cor, width=3 * e)
    return img.resize((64, 64), Image.LANCZOS)


class App:
    def __init__(self):
        self.cfg = config.carregar()
        self.raiz = tk.Tk()
        self.raiz.withdraw()
        self.gravador = audio.Gravador(self.cfg.microfone)
        self.transcritor = Transcritor()
        self.pilula = Pilula(self.raiz, nivel=lambda: self.gravador.nivel)
        self.fila: queue.Queue = queue.Queue()
        self.pronto = False
        self.tecla_presa = False
        self.bandeja = None

    # ---------- interface (sempre na thread do tkinter) ----------
    def ui(self, func, *args):
        self.raiz.after(0, func, *args)

    # ---------- modelo ----------
    def carregar_modelo(self):
        self.pronto = False
        nome = config.MODELOS.get(self.cfg.modelo, "auto")
        self.ui(self.pilula.aviso, "Preparando o modelo de voz… (só na 1ª vez demora)", 600)
        try:
            self.transcritor.carregar(nome)
        except Exception as e:
            self.ui(self.pilula.aviso, f"Erro ao carregar o modelo: {e}"[:80], 6)
            return
        self.pronto = True
        tecla = NOMES_TECLAS.get(self.cfg.atalho, self.cfg.atalho)
        acao = "Segure" if self.cfg.modo == "segurar" else "Aperte"
        self.ui(self.pilula.aviso, f"Pronto! {acao} {tecla} para falar", 3.5)
        self.atualizar_bandeja()

    # ---------- atalho ----------
    def _e_atalho(self, tecla) -> bool:
        nome = getattr(tecla, "name", None) or getattr(tecla, "char", None)
        return nome == self.cfg.atalho

    def ao_apertar(self, tecla):
        if not self._e_atalho(tecla) or self.tecla_presa:
            return
        self.tecla_presa = True
        if self.cfg.modo == "segurar":
            self.comecar()
        elif self.gravador.gravando:
            self.terminar()
        else:
            self.comecar()

    def ao_soltar(self, tecla):
        if not self._e_atalho(tecla):
            return
        self.tecla_presa = False
        if self.cfg.modo == "segurar" and self.gravador.gravando:
            self.terminar()

    def comecar(self):
        if not self.pronto:
            self.ui(self.pilula.aviso, "Ainda preparando o modelo…", 2)
            return
        try:
            self.gravador.iniciar()
        except Exception:
            self.ui(self.pilula.aviso, "Não achei o microfone", 3)
            return
        if self.cfg.som:
            audio.bipe(True)
        self.ui(self.pilula.ouvindo)

    def terminar(self):
        som = self.gravador.parar()
        if self.cfg.som:
            audio.bipe(False)
        if len(som) < audio.TAXA * 0.3:
            self.ui(self.pilula.esconder)
            return
        self.ui(self.pilula.pensando)
        self.fila.put(som)

    # ---------- trabalho pesado fora da interface ----------
    def trabalhador(self):
        while True:
            som = self.fila.get()
            try:
                texto = self.transcritor.transcrever(som, self.cfg.idioma)
            except Exception as e:
                self.ui(self.pilula.aviso, f"Erro: {e}"[:80], 4)
                continue
            if not texto:
                self.ui(self.pilula.aviso, "Não entendi nada. Tente de novo.", 2)
                continue
            colar.colar(texto + " ", self.cfg.restaurar_area)
            self.ui(self.pilula.pronto, len(texto.split()))
            with open(config.HISTORICO, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.datetime.now():%d/%m %H:%M}] {texto}\n")

    # ---------- bandeja ----------
    def atualizar_bandeja(self):
        if self.bandeja:
            self.bandeja.title = f"Ditado BR · {self.transcritor.dispositivo}" if self.pronto else "Ditado BR · preparando…"
            self.bandeja.update_menu()

    def _mudar(self, campo, valor, recarregar=False):
        def acao(icon, item):
            setattr(self.cfg, campo, valor)
            config.salvar(self.cfg)
            if recarregar:
                threading.Thread(target=self.carregar_modelo, daemon=True).start()
            if campo == "microfone":
                self.gravador.microfone = valor
            self.atualizar_bandeja()
        return acao

    def _marcado(self, campo, valor):
        return lambda item: getattr(self.cfg, campo) == valor

    def menu(self):
        M, I = pystray.Menu, pystray.MenuItem
        teclas = [I(n, self._mudar("atalho", k), checked=self._marcado("atalho", k), radio=True) for k, n in NOMES_TECLAS.items()]
        mics = [I("Padrão do Windows", self._mudar("microfone", None), checked=self._marcado("microfone", None), radio=True)]
        mics += [I(n[:45], self._mudar("microfone", i), checked=self._marcado("microfone", i), radio=True) for i, n in audio.microfones()]
        return M(
            I(lambda item: "Pronto para ditar" if self.pronto else "Preparando…", None, enabled=False),
            M.SEPARATOR,
            I("Tecla", M(*teclas)),
            I("Modo", M(
                I("Segurar para falar", self._mudar("modo", "segurar"), checked=self._marcado("modo", "segurar"), radio=True),
                I("Apertar para começar e parar", self._mudar("modo", "alternar"), checked=self._marcado("modo", "alternar"), radio=True))),
            I("Qualidade", M(
                I("Automática (recomendado)", self._mudar("modelo", "auto", True), checked=self._marcado("modelo", "auto"), radio=True),
                I("Rápida (modelo small)", self._mudar("modelo", "rapido", True), checked=self._marcado("modelo", "rapido"), radio=True),
                I("Precisa (large-v3-turbo)", self._mudar("modelo", "preciso", True), checked=self._marcado("modelo", "preciso"), radio=True))),
            I("Microfone", M(*mics)),
            I("Bipe ao gravar", lambda i, it: self._alternar("som"), checked=lambda it: self.cfg.som),
            M.SEPARATOR,
            I("Editar dicionário…", lambda: os.startfile(config.DICIONARIO)),
            I("Ver histórico…", lambda: os.path.exists(config.HISTORICO) and os.startfile(config.HISTORICO)),
            I("Iniciar com o Windows", lambda i, it: self._alternar_inicio(), checked=lambda it: inicia_com_windows()),
            M.SEPARATOR,
            I("Sair", self.sair),
        )

    def _alternar(self, campo):
        setattr(self.cfg, campo, not getattr(self.cfg, campo))
        config.salvar(self.cfg)

    def _alternar_inicio(self):
        definir_inicio(not inicia_com_windows())

    def sair(self, *_):
        if self.bandeja:
            self.bandeja.stop()
        self.raiz.after(0, self.raiz.destroy)

    def rodar(self):
        self.bandeja = pystray.Icon("ditado-br", icone(), "Ditado BR · preparando…", self.menu())
        self.bandeja.run_detached()
        threading.Thread(target=self.carregar_modelo, daemon=True).start()
        threading.Thread(target=self.trabalhador, daemon=True).start()
        ouvinte = keyboard.Listener(on_press=self.ao_apertar, on_release=self.ao_soltar)
        ouvinte.daemon = True
        ouvinte.start()
        self.raiz.mainloop()


# ---------- iniciar com o Windows ----------
def inicia_com_windows() -> bool:
    return atalhos.existe("inicio")


def definir_inicio(ligar: bool):
    if ligar:
        if not os.path.exists(atalhos.ICONE):
            atalhos.criar_icone()
        atalhos.criar("inicio")
    else:
        atalhos.remover("inicio")


def principal():
    # um único Ditado por vez
    ctypes.windll.kernel32.CreateMutexW(None, False, "DitadoBR_unico")
    if ctypes.windll.kernel32.GetLastError() == 183:
        ctypes.windll.user32.MessageBoxW(0, "O Ditado BR já está aberto (ícone perto do relógio).", "Ditado BR", 0x40)
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    App().rodar()
