"""Configurações do usuário, salvas em %APPDATA%/ditado-br."""

import json
import os
from dataclasses import asdict, dataclass, field

PASTA = os.environ.get("DITADO_PASTA") or os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "ditado-br")
ARQUIVO = os.path.join(PASTA, "config.json")
DICIONARIO = os.path.join(PASTA, "dicionario.txt")
HISTORICO = os.path.join(PASTA, "historico.txt")

DICIONARIO_PADRAO = """# Dicionário do Ditado BR
# Uma linha por termo. O Whisper passa a escrever estes nomes do jeito certo.
# Para trocar uma palavra por outra, use:  errado => certo
Claude Code
YouTube
TikTok
Instagram
Reels
Shorts
WhatsApp
GitHub
cloud code => Claude Code
"""

MODELOS = {
    "auto": "auto",                 # preciso na placa de vídeo, leve no processador
    "rapido": "small",              # leve, roda bem em qualquer PC
    "preciso": "large-v3-turbo",    # melhor qualidade, ideal com placa de vídeo
}


@dataclass
class Config:
    atalho: str = "ctrl_r"          # tecla para segurar e falar
    modo: str = "segurar"           # segurar | alternar
    modelo: str = "auto"            # auto | rapido | preciso
    idioma: str = "pt"
    som: bool = True                # bipe ao começar e terminar
    restaurar_area: bool = True     # devolve o que estava na área de transferência
    microfone: int | None = None    # None = padrão do Windows
    extras: dict = field(default_factory=dict)


def carregar() -> Config:
    os.makedirs(PASTA, exist_ok=True)
    if not os.path.exists(DICIONARIO):
        with open(DICIONARIO, "w", encoding="utf-8") as f:
            f.write(DICIONARIO_PADRAO)
    if os.path.exists(ARQUIVO):
        try:
            dados = json.load(open(ARQUIVO, encoding="utf-8"))
            return Config(**{k: v for k, v in dados.items() if k in Config.__dataclass_fields__})
        except (ValueError, TypeError):
            pass
    cfg = Config()
    salvar(cfg)
    return cfg


def salvar(cfg: Config):
    os.makedirs(PASTA, exist_ok=True)
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(asdict(cfg), f, ensure_ascii=False, indent=2)


def ler_dicionario() -> tuple[list[str], dict[str, str]]:
    """Devolve (termos que o Whisper deve conhecer, trocas 'errado' -> 'certo')."""
    termos, trocas = [], {}
    if not os.path.exists(DICIONARIO):
        return termos, trocas
    for linha in open(DICIONARIO, encoding="utf-8"):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        if "=>" in linha:
            errado, certo = (p.strip() for p in linha.split("=>", 1))
            if errado and certo:
                trocas[errado] = certo
                termos.append(certo)
        else:
            termos.append(linha)
    return termos, trocas
