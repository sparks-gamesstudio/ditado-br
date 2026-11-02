"""Atalhos do Windows: Menu Iniciar, Área de Trabalho e inicialização automática."""

import os
import subprocess
import sys

PASTA_APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONE = os.path.join(PASTA_APP, "ditado.ico")
NOME = "Ditado BR.lnk"


def _pastas() -> dict[str, str]:
    appdata = os.environ["APPDATA"]
    return {
        "menu": os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs"),
        "inicio": os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup"),
        "area": os.path.join(os.path.expanduser("~"), "Desktop"),
    }


def _pythonw() -> str:
    return os.path.join(os.path.dirname(sys.executable), "pythonw.exe")


def criar_icone():
    from .app import icone
    img = icone()
    img.save(ICONE, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64)])


def criar(onde: str):
    destino = os.path.join(_pastas()[onde], NOME)
    script = (
        "$s=(New-Object -ComObject WScript.Shell).CreateShortcut($env:DESTINO);"
        "$s.TargetPath=$env:ALVO;$s.Arguments='-m ditado';$s.WorkingDirectory=$env:PASTA;"
        "$s.IconLocation=$env:ICONE;$s.Description='Ditado BR: fale e o texto aparece';$s.Save()"
    )
    env = {**os.environ, "DESTINO": destino, "ALVO": _pythonw(), "PASTA": PASTA_APP, "ICONE": ICONE}
    subprocess.run(["powershell", "-NoProfile", "-Command", script], env=env, check=True,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def existe(onde: str) -> bool:
    return os.path.exists(os.path.join(_pastas()[onde], NOME))


def remover(onde: str):
    caminho = os.path.join(_pastas()[onde], NOME)
    if os.path.exists(caminho):
        os.remove(caminho)


if __name__ == "__main__":
    criar_icone()
    criar("menu")
    criar("area")
    print("   Atalhos criados no Menu Iniciar e na Area de Trabalho.")
