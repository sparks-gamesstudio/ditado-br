"""Escreve o texto onde o cursor está: põe na área de transferência e aperta Ctrl+V."""

import threading
import time

import pyperclip
from pynput.keyboard import Controller, Key

_teclado = Controller()


def colar(texto: str, restaurar: bool = True):
    if not texto:
        return
    anterior = None
    if restaurar:
        try:
            anterior = pyperclip.paste()
        except Exception:
            anterior = None
    pyperclip.copy(texto)
    time.sleep(0.05)
    with _teclado.pressed(Key.ctrl):
        _teclado.press("v")
        _teclado.release("v")
    if restaurar and anterior is not None:
        # espera o app ler a área de transferência antes de devolver o conteúdo antigo
        threading.Timer(0.6, lambda: pyperclip.copy(anterior)).start()
