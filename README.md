<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0B0A09,100:D97757&height=170&section=header&text=Ditado%20BR&fontSize=52&fontColor=F3EDE6&fontAlignY=36&desc=fale%20e%20o%20texto%20aparece%20%C2%B7%20gr%C3%A1tis%20da%20F%C3%A1brica%20de%20Canais&descAlignY=58&descSize=17" width="100%" alt="Ditado BR" />

<img src="docs/icone.png" width="96" alt="Ícone do Ditado BR" />

**Segure uma tecla, fale em português e o texto aparece onde o cursor estiver.**<br/>
WhatsApp, Word, e-mail, Claude Code, ChatGPT, qualquer programa.

<p>
  <img src="https://img.shields.io/badge/100%25%20offline-D97757?style=for-the-badge" alt="100% offline" />
  <img src="https://img.shields.io/badge/gr%C3%A1tis-0B0A09?style=for-the-badge" alt="Grátis" />
  <img src="https://img.shields.io/badge/sem%20conta-F3EDE6?style=for-the-badge" alt="Sem conta" />
  <img src="https://img.shields.io/badge/sem%20limite%20de%20uso-0B0A09?style=for-the-badge" alt="Sem limite de uso" />
</p>

<p>
  <a href="https://github.com/sparks-gamesstudio/ditado-br/archive/refs/heads/main.zip"><img src="https://img.shields.io/badge/%E2%AC%87%EF%B8%8F%20Baixar%20para%20Windows-D97757?style=for-the-badge&logo=windows&logoColor=white" alt="Baixar para Windows" /></a>
  <a href="https://sparks-gamesstudio.github.io/fabrica-de-canais/github.html"><img src="https://img.shields.io/badge/Mais%20projetos%20gr%C3%A1tis-0B0A09?style=for-the-badge&logo=github&logoColor=D97757" alt="Mais projetos grátis" /></a>
  <img src="https://img.shields.io/github/stars/sparks-gamesstudio/ditado-br?style=for-the-badge&color=D97757&label=%E2%AD%90" alt="Estrelas" />
</p>

<img src="docs/estados.png" width="360" alt="A janelinha do Ditado: ouvindo, transcrevendo, pronto" />

</div>

## 👋 O Rebite explica

<img align="right" src="https://raw.githubusercontent.com/sparks-gamesstudio/sparks-gamesstudio/main/assets/rebite/acenar.jpg" width="170" alt="Rebite, o mascote da Fábrica de Canais" />

> Digitar mensagem comprida cansa, né? Com o Ditado você só segura uma tecla e fala. Solta, e o texto já está lá, com ponto, vírgula e acento. E fica tudo no seu PC: sua voz não vai para lugar nenhum.

<br clear="right" />

## 🎙️ Como usa

1. **Segure o Ctrl direito** e fale.
2. **Solte.** Em 1 a 2 segundos o texto aparece, já com pontuação e acentos.

<table>
<tr>
<td width="110" align="center"><img src="https://raw.githubusercontent.com/sparks-gamesstudio/sparks-gamesstudio/main/assets/rebite/joinha.jpg" width="90" alt="Rebite" /></td>
<td>

**Só isso.** Uma janelinha discreta mostra a sua voz enquanto você fala e some quando termina. Ela nunca rouba o foco do programa em que você está.

</td>
</tr>
</table>

## ✨ Por que usar

- **Sua voz não sai do PC.** A transcrição roda na sua máquina com o [Whisper](https://github.com/openai/whisper), sem nuvem e sem assinatura.
- **Escreve nomes difíceis certo.** No dicionário você ensina os termos do seu trabalho (`Claude Code`, nomes de clientes, gírias) e corrige o que ele ouvir errado (`cloud code => Claude Code`).
- **Rápido de verdade.** Com placa de vídeo NVIDIA, 4 segundos de fala viram texto em ~1,7 s com o modelo mais preciso (testado numa GTX 1650 de 4 GB). Sem placa, usa um modelo mais leve no processador.
- **Não apaga o que você copiou.** Depois de colar, ele devolve o conteúdo antigo da área de transferência.

<a id="instalacao"></a>

## ⬇️ Instalação (Windows)

1. Instale o [Python 3.10 ou mais novo](https://www.python.org/downloads/) marcando **"Add python.exe to PATH"**.
2. [Baixe este repositório](https://github.com/sparks-gamesstudio/ditado-br/archive/refs/heads/main.zip) e descompacte.
3. Dê dois cliques em **`instalar.bat`**.

O instalador cria um ambiente isolado (não mexe no resto do seu Python), detecta se você tem placa NVIDIA e cria atalhos no Menu Iniciar e na Área de Trabalho. Na primeira vez que abrir, o Ditado baixa o modelo de voz (1,6 GB com placa de vídeo, 500 MB sem).

## ⚙️ Configurações

Clique com o botão direito no ícone perto do relógio:

| Opção | O que faz |
|---|---|
| **Tecla** | Ctrl direito, AltGr, F8, F9, Caps Lock, Scroll Lock ou Pause |
| **Modo** | *Segurar para falar* ou *Apertar para começar e parar* (bom para textos longos) |
| **Qualidade** | *Automática* escolhe sozinha. *Rápida* é a melhor opção se a sua placa vive ocupada com jogos ou com o Wallpaper Engine |
| **Microfone** | escolha qual usar |
| **Editar dicionário** | termos e correções (abre no Bloco de Notas) |
| **Ver histórico** | tudo o que você ditou, com data e hora |
| **Iniciar com o Windows** | abre sozinho quando o PC liga |

## 🧑‍💻 Para quem gosta de código

```bash
git clone https://github.com/sparks-gamesstudio/ditado-br.git
cd ditado-br
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-nvidia.txt   # opcional, só com placa NVIDIA
python -m ditado
```

| Arquivo | O que faz |
|---|---|
| `ditado/app.py` | tecla de atalho, ícone na bandeja e fila de transcrição |
| `ditado/audio.py` | gravação a 16 kHz e nível de volume ao vivo |
| `ditado/transcrever.py` | faster-whisper, com placa de vídeo primeiro e processador como reserva, além do dicionário |
| `ditado/janela.py` | a pílula flutuante que não rouba o foco |
| `ditado/colar.py` | cola no programa ativo e devolve a área de transferência |

## 🙏 Créditos

Inspirado no [Handy](https://github.com/cjpais/Handy) (MIT). Código escrito do zero, em Python, pensado para o Windows e o português do Brasil. Transcrição com [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

---

<div align="center">

<a href="https://sparks-gamesstudio.github.io/fabrica-de-canais/"><img src="https://sparks-gamesstudio.github.io/fabrica-de-canais/marca/simbolo-1024.png" width="56" alt="Fábrica de Canais" /></a>

Feito pela **[Fábrica de Canais](https://sparks-gamesstudio.github.io/fabrica-de-canais/)**, skills de Claude Code para canais de vídeo no piloto automático.

<a href="https://instagram.com/afabricadecanais"><img src="https://img.shields.io/badge/@afabricadecanais-E4405F?style=flat-square&logo=instagram&logoColor=white" alt="Instagram" /></a>
<a href="https://github.com/sparks-gamesstudio"><img src="https://img.shields.io/badge/mais%20projetos-0B0A09?style=flat-square&logo=github&logoColor=D97757" alt="Mais projetos" /></a>

<sub>Licença MIT · use, modifique e compartilhe. Se ajudou, deixa uma ⭐</sub>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:D97757,100:0B0A09&height=90&section=footer" width="100%" alt="" />

</div>
