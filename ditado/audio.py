"""Gravação do microfone (16 kHz, mono) com nível de volume ao vivo para a animação."""

import threading

import numpy as np
import sounddevice as sd

TAXA = 16000


class Gravador:
    def __init__(self, microfone: int | None = None):
        self.microfone = microfone
        self._blocos: list[np.ndarray] = []
        self._fluxo = None
        self._trava = threading.Lock()
        self.nivel = 0.0  # 0..1, lido pela janelinha

    def _callback(self, dados, quadros, tempo, status):
        bloco = dados[:, 0].copy()
        with self._trava:
            self._blocos.append(bloco)
        rms = float(np.sqrt(np.mean(bloco ** 2)))
        self.nivel = min(1.0, rms * 12)

    def iniciar(self):
        with self._trava:
            self._blocos = []
        self._fluxo = sd.InputStream(samplerate=TAXA, channels=1, dtype="float32",
                                     device=self.microfone, blocksize=800, callback=self._callback)
        self._fluxo.start()

    def parar(self) -> np.ndarray:
        if self._fluxo is not None:
            self._fluxo.stop()
            self._fluxo.close()
            self._fluxo = None
        self.nivel = 0.0
        with self._trava:
            audio = np.concatenate(self._blocos) if self._blocos else np.zeros(0, dtype=np.float32)
            self._blocos = []
        return audio

    @property
    def gravando(self) -> bool:
        return self._fluxo is not None


def microfones() -> list[tuple[int, str]]:
    vistos, lista = set(), []
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0 and d["hostapi"] == 0 and d["name"] not in vistos:
            vistos.add(d["name"])
            lista.append((i, d["name"]))
    return lista


def bipe(subindo: bool = True):
    """Bipe curto e suave, sem arquivo de som."""
    dur = 0.07
    t = np.linspace(0, dur, int(44100 * dur), endpoint=False)
    f0, f1 = (660, 990) if subindo else (990, 660)
    onda = np.sin(2 * np.pi * np.linspace(f0, f1, t.size) * t) * np.hanning(t.size) * 0.18
    try:
        sd.play(onda.astype(np.float32), 44100)
    except Exception:
        pass
