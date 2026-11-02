"""Janelinha flutuante (pílula) na parte de baixo da tela.

Nunca rouba o foco: o texto tem que ir para o app em que você estava.
"""

import ctypes
import math
import time
import tkinter as tk

from PIL import Image, ImageDraw, ImageTk

L, A = 260, 56          # tamanho da pílula
CHAVE = "#010203"       # cor que vira transparente
FUNDO = (20, 20, 22)
TEXTO = "#EDEDED"
SUAVE = "#9A9A9F"
VERMELHO = "#FF4D4D"
LARANJA = "#FF7A45"
VERDE = "#46D37E"
BARRAS = 22


def _pilula() -> Image.Image:
    # desenha em 4x e reduz: borda lisa mesmo com a cor-chave
    e = 4
    img = Image.new("RGB", (L * e, A * e), (1, 2, 3))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, L * e - 1, A * e - 1], radius=A * e // 2, fill=FUNDO, outline=(60, 60, 64), width=e)
    return img.resize((L, A), Image.LANCZOS)


def _sem_foco(janela: tk.Toplevel):
    GWL_EXSTYLE, WS_EX_NOACTIVATE, WS_EX_TOOLWINDOW, WS_EX_TRANSPARENT = -20, 0x08000000, 0x80, 0x20
    hwnd = ctypes.windll.user32.GetParent(janela.winfo_id())
    estilo = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, estilo | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TRANSPARENT)


class Pilula:
    def __init__(self, raiz: tk.Tk, nivel=lambda: 0.0):
        self.nivel = nivel
        self.estado = "oculto"
        self.mensagem = ""
        self._inicio = 0.0
        self._historico = [0.0] * BARRAS
        self._esconder_em = 0.0

        j = self.janela = tk.Toplevel(raiz)
        j.overrideredirect(True)
        j.attributes("-topmost", True)
        j.configure(bg=CHAVE)
        j.attributes("-transparentcolor", CHAVE)
        larg, alt = j.winfo_screenwidth(), j.winfo_screenheight()
        j.geometry(f"{L}x{A}+{(larg - L) // 2}+{alt - A - 90}")
        self.tela = tk.Canvas(j, width=L, height=A, bg=CHAVE, highlightthickness=0)
        self.tela.pack()
        self._fundo = ImageTk.PhotoImage(_pilula())
        j.update_idletasks()
        _sem_foco(j)
        j.withdraw()
        self._animar()

    # chamados pelo app (em qualquer thread, via after)
    def ouvindo(self):
        self._mostrar("ouvindo")

    def pensando(self):
        self._mostrar("pensando")

    def pronto(self, palavras: int):
        self.mensagem = f"{palavras} palavra{'s' if palavras != 1 else ''}"
        self._mostrar("pronto", segundos=1.1)

    def aviso(self, texto: str, segundos: float = 2.5):
        self.mensagem = texto
        self._mostrar("aviso", segundos=segundos)

    def esconder(self):
        self.estado = "oculto"
        self.janela.withdraw()

    def _mostrar(self, estado: str, segundos: float = 0):
        self.estado = estado
        self._inicio = time.time()
        self._esconder_em = time.time() + segundos if segundos else 0
        self.janela.deiconify()
        self.janela.attributes("-topmost", True)

    def _animar(self):
        if self.estado != "oculto":
            if self._esconder_em and time.time() > self._esconder_em:
                self.esconder()
            else:
                self._desenhar()
        self.janela.after(33, self._animar)

    def _desenhar(self):
        c = self.tela
        c.delete("all")
        c.create_image(0, 0, image=self._fundo, anchor="nw")
        t = time.time() - self._inicio
        meio = A / 2

        if self.estado == "ouvindo":
            pulso = 5 + 1.5 * math.sin(t * 6)
            c.create_oval(26 - pulso, meio - pulso, 26 + pulso, meio + pulso, fill=VERMELHO, outline="")
            self._historico = self._historico[1:] + [self.nivel()]
            x0, passo = 48, 7
            for i, v in enumerate(self._historico):
                h = 3 + v * 30
                x = x0 + i * passo
                c.create_line(x, meio - h / 2, x, meio + h / 2, fill=TEXTO if v > 0.05 else SUAVE, width=3, capstyle="round")
            seg = int(t)
            c.create_text(L - 26, meio, text=f"{seg // 60}:{seg % 60:02d}", fill=SUAVE, font=("Segoe UI", 10), anchor="e")

        elif self.estado == "pensando":
            for i in range(3):
                fase = (t * 3 - i * 0.35) % 2
                r = 3 + 2.5 * max(0.0, math.sin(min(fase, 1) * math.pi))
                x = 32 + i * 16
                c.create_oval(x - r, meio - r, x + r, meio + r, fill=LARANJA, outline="")
            c.create_text(78, meio, text="Transcrevendo…", fill=TEXTO, font=("Segoe UI Semibold", 11), anchor="w")

        elif self.estado == "pronto":
            c.create_line(22, meio, 29, meio + 7, 42, meio - 7, fill=VERDE, width=3, capstyle="round", joinstyle="round")
            c.create_text(56, meio, text="Pronto", fill=TEXTO, font=("Segoe UI Semibold", 11), anchor="w")
            c.create_text(L - 26, meio, text=self.mensagem, fill=SUAVE, font=("Segoe UI", 10), anchor="e")

        elif self.estado == "aviso":
            c.create_text(L / 2, meio, text=self.mensagem, fill=TEXTO, font=("Segoe UI Semibold", 10), width=L - 40)
