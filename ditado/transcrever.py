"""Transcrição local com faster-whisper. Tenta a placa de vídeo e cai para o processador."""

import os
import re
import threading

import numpy as np

from . import config

TAXA = 16000


def _bibliotecas_nvidia():
    """Deixa o Windows achar cuBLAS/cuDNN instalados via pip (pacotes nvidia-*)."""
    try:
        import nvidia
    except ImportError:
        return
    for raiz in nvidia.__path__:
        for pacote in os.listdir(raiz):
            pasta = os.path.join(raiz, pacote, "bin")
            if os.path.isdir(pasta):
                os.add_dll_directory(pasta)
                os.environ["PATH"] = pasta + os.pathsep + os.environ.get("PATH", "")


_bibliotecas_nvidia()


class Transcritor:
    def __init__(self):
        self._modelo = None
        self._nome = None
        self.dispositivo = "?"
        self._trava = threading.Lock()

    def carregar(self, nome: str):
        """Carrega o modelo (baixa na primeira vez). Seguro chamar várias vezes.

        nome "auto": large-v3-turbo na placa de vídeo, small no processador.
        int8_float16 vem antes de float16: em placas de 4 GB é até 4x mais rápido.
        """
        with self._trava:
            if self._nome == nome and self._modelo is not None:
                return
            from faster_whisper import WhisperModel

            gpu = "large-v3-turbo" if nome == "auto" else nome
            cpu = "small" if nome == "auto" else nome
            self._modelo = None
            for dispositivo, tipo, arquivo in (("cuda", "int8_float16", gpu), ("cuda", "float16", gpu), ("cpu", "int8", cpu)):
                try:
                    modelo = WhisperModel(arquivo, device=dispositivo, compute_type=tipo)
                    # um teste curto: alguns PCs só falham na primeira transcrição de verdade
                    list(modelo.transcribe(np.zeros(TAXA, dtype=np.float32), language="pt")[0])
                    self._modelo, self._nome = modelo, nome
                    self.dispositivo = ("placa de vídeo" if dispositivo == "cuda" else "processador") + f" · {arquivo}"
                    return
                except Exception:
                    continue
            raise RuntimeError(f"Não consegui carregar o modelo {nome}.")

    def transcrever(self, audio: np.ndarray, idioma: str = "pt") -> str:
        if self._modelo is None:
            raise RuntimeError("Modelo ainda não carregado.")
        if len(audio) < TAXA * 0.3 or float(np.abs(audio).max()) < 0.01:
            return ""  # toque acidental ou silêncio
        termos, trocas = config.ler_dicionario()
        dica = ", ".join(termos[:60]) + "." if termos else None
        with self._trava:
            segmentos, _ = self._modelo.transcribe(
                audio, language=idioma, beam_size=1, vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500},
                initial_prompt=dica, condition_on_previous_text=False,
            )
            texto = " ".join(s.text.strip() for s in segmentos).strip()
        return limpar(texto, trocas)


ALUCINACOES = (
    "legendas pela comunidade amara.org", "obrigado por assistir", "inscreva-se no canal",
    "legenda adriana zanotto", "tchau, tchau",
)


def limpar(texto: str, trocas: dict[str, str]) -> str:
    # o Whisper às vezes "ouve" frases de fim de vídeo no silêncio
    if texto.lower().strip(" .!") in ALUCINACOES:
        return ""
    for errado, certo in trocas.items():
        texto = re.sub(rf"\b{re.escape(errado)}\b", certo, texto, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", texto).strip()
