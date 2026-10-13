"""
PARTE 3 — Animação das iterações de cada método.

Para cada método, um gráfico que se atualiza a cada iteração:
    - à esquerda, a curva de f com a "construção" do passo k
      (intervalo, corda, tangente ou secante) e o novo xₖ,
      com zoom automático acompanhando a convergência;
    - à direita, |f(xₖ)| em escala log, crescendo a cada iteração.

Não recalcula nada por conta própria: roda os métodos de verdade e
remonta cada passo a partir do Resultado.historico (mesma regra de
atualização do intervalo usada em metodos_intervalo.py).

Como usar:
    python animacao.py          # Problema 2 (circuito RC): abre as 4 animações
    python animacao.py --salvar # salva os vídeos MP4 em docs/animacoes/ (precisa do ffmpeg)
    python animacao.py --gif    # salva GIFs em vez de MP4
    python animacao.py 1        # outro caso de casos.py (1 = exemplo, 2 = Problema 1...)
"""

import argparse
import math
import os
import re
import sys
import time
import webbrowser
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.backend_tools import Cursors

from casos import CASOS, EPS_PADRAO, MAX_ITER_PADRAO
from entrada import ler_funcao
from metodos_abertos import newton_raphson, secante
from metodos_intervalo import bisseccao, falsa_posicao
from relatorio import (COR_FUNDO, COR_GRADE, COR_RAIZ, COR_TEXTO,
                       COR_TEXTO_SECUNDARIO, CORES_METODOS, _valor_seguro)
from resultado import Resultado

FPS = 30
QUADROS_INICIO = 30    # 1 s mostrando o estado inicial
QUADROS_ZOOM = 15      # zoom suave até a região do próximo passo
QUADROS_DESENHO = 15   # a reta (ou o ponto médio) "caminha" até o novo xₖ
QUADROS_PAUSA = 12     # parado mostrando o novo xₖ e f(xₖ)
QUADROS_FINAL = 90     # 3 s no fim, com a raiz encontrada

MARGEM = 0.35             # folga de cada lado da janela, em fração da largura
ZOOM_MAX_POR_PASSO = 2.5  # aproxima no máximo 2,5x por iteração (fica menos "colado")

SUBSCRITOS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def _sub(k: int) -> str:
    """Número em subscrito: 12 -> '₁₂'."""
    return str(k).translate(SUBSCRITOS)


def _suave(t: float) -> float:
    """Faz o movimento começar e terminar devagar (0 -> 0, 1 -> 1)."""
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------------------
# Passos: o que desenhar em cada iteração
# ---------------------------------------------------------------------------

def montar_passos(f: Callable[[float], float], resultado: Resultado,
                  caso: dict) -> list[dict]:
    """
    Remonta, a partir do histórico, o que cada método "usou" para gerar xₖ.

    Cada passo é um dict com:
        x         -> o novo xₖ
        pontos    -> abscissas usadas na construção (a e b, ou os x anteriores)
        a, b      -> intervalo (só nos métodos de intervalo)
    """
    passos = []
    h = resultado.historico

    if resultado.metodo in ("Bissecção", "Falsa Posição"):
        a, b = caso["a"], caso["b"]
        parado_a = parado_b = 0  # há quantas iterações cada ponta não muda
        anterior = None
        for x in h:
            passo = {"x": x, "a": a, "b": b, "pontos": [a, b],
                     "parado_a": parado_a, "parado_b": parado_b}
            # Na Falsa Posição uma ponta pode ficar parada para sempre (função
            # côncava ou convexa); então o zoom acompanha só a ponta que anda,
            # que é a aproximação anterior
            if resultado.metodo == "Falsa Posição" and anterior is not None:
                passo["foco"] = [anterior]
            passos.append(passo)

            # Mesma regra de atualização de metodos_intervalo.py
            if f(a) * f(x) < 0:
                b = x
                parado_a, parado_b = parado_a + 1, 0
            else:
                a = x
                parado_a, parado_b = 0, parado_b + 1
            anterior = x

    elif resultado.metodo == "Newton-Raphson":
        anteriores = [caso["x0_newton"]] + h[:-1]
        for anterior, x in zip(anteriores, h):
            passos.append({"x": x, "pontos": [anterior]})

    elif resultado.metodo == "Secante":
        s = [caso["x0_secante"], caso["x1_secante"]] + h
        for k, x in enumerate(h):
            passos.append({"x": x, "pontos": [s[k], s[k + 1]]})

    return passos


def _janela_inicial(caso: dict) -> tuple[float, float]:
    """O intervalo [a, b] e os chutes iniciais, com uma pequena folga."""
    xs = [caso["a"], caso["b"], caso["x0_newton"], caso["x0_secante"], caso["x1_secante"]]
    inicio, fim = min(xs), max(xs)
    folga = (fim - inicio) * 0.1
    return inicio - folga, fim + folga


def _janela_do_passo(passo: dict, anterior: tuple[float, float],
                     inicial: tuple[float, float]) -> tuple[float, float]:
    """
    Janela do eixo x para o passo: mostra a construção e o novo xₖ com
    folga, sem aproximar mais que ZOOM_MAX_POR_PASSO em relação à janela
    anterior e sem ficar maior que a janela inicial.
    """
    xs = passo.get("foco", passo["pontos"]) + [passo["x"]]
    inicio, fim = min(xs), max(xs)
    centro = (inicio + fim) / 2
    largura = max(fim - inicio, 1e-12 * max(1.0, abs(centro))) * (1 + 2 * MARGEM)
    largura = max(largura, (anterior[1] - anterior[0]) / ZOOM_MAX_POR_PASSO)
    largura = min(largura, inicial[1] - inicial[0])
    return centro - largura / 2, centro + largura / 2


def _interpolar_janela(j0, j1, t: float) -> tuple[float, float]:
    """Zoom suave: centro anda em linha reta e a largura muda em escala log."""
    t = _suave(t)
    c0, c1 = (j0[0] + j0[1]) / 2, (j1[0] + j1[1]) / 2
    l0, l1 = j0[1] - j0[0], j1[1] - j1[0]
    centro = c0 + (c1 - c0) * t
    largura = math.exp(math.log(l0) + (math.log(l1) - math.log(l0)) * t)
    return centro - largura / 2, centro + largura / 2


def _roteiro(passos: list[dict], caso: dict) -> list[tuple]:
    """
    Lista de quadros da animação. Cada quadro é (k, janela, fase, t):
        k      -> índice do passo (0 = estado inicial, antes da 1ª iteração)
        janela -> limites do eixo x neste quadro
        fase   -> "zoom", "desenho" ou "pausa" (o novo xₖ só aparece na pausa)
        t      -> progresso dentro da fase, de 0 a 1
    """
    inicial = _janela_inicial(caso)
    quadros = [(0, inicial, "pausa", 1.0)] * QUADROS_INICIO
    janela_atual = inicial

    for k, passo in enumerate(passos, start=1):
        nova = _janela_do_passo(passo, janela_atual, inicial)
        for i in range(1, QUADROS_ZOOM + 1):
            t = i / QUADROS_ZOOM
            quadros.append((k, _interpolar_janela(janela_atual, nova, t), "zoom", t))
        for i in range(1, QUADROS_DESENHO + 1):
            quadros.append((k, nova, "desenho", i / QUADROS_DESENHO))
        for i in range(1, QUADROS_PAUSA + 1):
            quadros.append((k, nova, "pausa", i / QUADROS_PAUSA))
        janela_atual = nova

    if passos:
        quadros += [(len(passos), janela_atual, "pausa", 1.0)] * QUADROS_FINAL
    return quadros


# ---------------------------------------------------------------------------
# Desenho de um quadro
# ---------------------------------------------------------------------------

def _estilizar(ax) -> None:
    ax.set_facecolor(COR_FUNDO)
    ax.tick_params(colors=COR_TEXTO_SECUNDARIO, labelsize=9)
    for borda in ax.spines.values():
        borda.set_color(COR_GRADE)
    ax.grid(color=COR_GRADE, linewidth=0.8)


def _desenhar_curva(ax, f, janela) -> None:
    """Curva de f na janela atual, com o eixo y ajustado a ela (e ao zero)."""
    xs = np.linspace(janela[0], janela[1], 400)
    ys = np.array([v if (v := _valor_seguro(f, x)) is not None else np.nan for x in xs])

    finitos = ys[np.isfinite(ys)]
    y_min = min(finitos.min(), 0) if finitos.size else -1
    y_max = max(finitos.max(), 0) if finitos.size else 1
    folga = (y_max - y_min) * 0.15 or 1.0

    ax.axhline(0, color=COR_TEXTO_SECUNDARIO, linewidth=1)
    ax.plot(xs, ys, color=COR_TEXTO, linewidth=2, zorder=2)
    ax.set_xlim(*janela)
    ax.set_ylim(y_min - folga, y_max + folga)
    ax.ticklabel_format(axis="x", useOffset=False)  # mostra t de verdade, mesmo com zoom


def _reta(ax, p0, p1, janela, cor, alpha=0.8) -> None:
    """Reta tracejada que passa por p0 e p1, esticada até as bordas da janela."""
    (x0, y0), (x1, y1) = p0, p1
    if x1 == x0:
        return
    inclinacao = (y1 - y0) / (x1 - x0)
    xs = np.array(janela)
    ax.plot(xs, y0 + inclinacao * (xs - x0), color=cor, linewidth=1.4,
            linestyle="--", alpha=alpha, zorder=3)


def _ponto(ax, x, y, cor, tamanho=7, vazio=False) -> None:
    ax.plot(x, y, marker="o", markersize=tamanho, zorder=5,
            color=COR_FUNDO if vazio else cor, markeredgecolor=cor if vazio else COR_FUNDO,
            markeredgewidth=1.8)


def _caminhar(ax, origem, destino, t: float, cor) -> None:
    """Trecho sólido de origem até origem + t·(destino - origem), com um ponto na ponta."""
    (x0, y0), (x1, y1) = origem, destino
    xt, yt = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
    ax.plot([x0, xt], [y0, yt], color=cor, linewidth=2.2, zorder=4)
    _ponto(ax, xt, yt, cor, tamanho=6)


def _rotulo(ax, texto, x, y, cor=COR_TEXTO_SECUNDARIO, abaixo=False, **kwargs) -> None:
    ax.annotate(texto, (x, y), textcoords="offset points", xytext=(6, -14 if abaixo else 6),
                color=cor, fontsize=9, **kwargs)


def _desenhar_geometria(ax, f, metodo: str, passos: list[dict], k: int, fase: str,
                        t: float, janela, caso: dict, cor: str) -> str:
    """Desenha o quadro do passo k e devolve o texto de informações."""
    _desenhar_curva(ax, f, janela)
    intervalo = metodo in ("Bissecção", "Falsa Posição")

    if k == 0:  # estado inicial, nenhuma iteração ainda
        if intervalo:
            a, b = caso["a"], caso["b"]
            ax.axvspan(a, b, color=cor, alpha=0.12, linewidth=0)
            for x, nome in ((a, "a"), (b, "b")):
                _ponto(ax, x, f(x), cor, vazio=True)
                _rotulo(ax, nome, x, f(x), abaixo=f(x) > 0)
            return f"Início:  [a, b] = [{a:g}, {b:g}]   f(a) = {f(a):.4g}   f(b) = {f(b):.4g}\n"
        iniciais = ([caso["x0_newton"]] if metodo == "Newton-Raphson"
                    else [caso["x0_secante"], caso["x1_secante"]])
        for i, x in enumerate(iniciais):
            ax.plot([x, x], [0, f(x)], color=cor, linewidth=1, linestyle=":")
            _ponto(ax, x, f(x), cor, vazio=True)
            _rotulo(ax, f"x{_sub(i)}", x, f(x))
        return ("Início:  " + "   ".join(f"x{_sub(i)} = {x:g}" for i, x in enumerate(iniciais))
                + "\n")

    passo = passos[k - 1]
    x = passo["x"]
    fx = f(x)
    # As linhas da construção aparecem aos poucos durante o zoom
    alpha = 0.8 * _suave(t) if fase == "zoom" else 0.8

    # Rastro: aproximações anteriores sobre o eixo
    for anterior in passos[:k - 1]:
        ax.plot(anterior["x"], 0, marker="|", markersize=10, color=cor, alpha=0.35, zorder=3)

    if intervalo:
        a, b = passo["a"], passo["b"]
        if fase == "zoom" and k > 1:  # o intervalo encolhe suavemente até o novo [a, b]
            antes = passos[k - 2]
            s = _suave(t)
            a = antes["a"] + (a - antes["a"]) * s
            b = antes["b"] + (b - antes["b"]) * s
        ax.axvspan(a, b, color=cor, alpha=0.12, linewidth=0)
        for ponta, nome in ((a, "a"), (b, "b")):
            ax.axvline(ponta, color=cor, linewidth=1, alpha=0.5)
            _ponto(ax, ponta, f(ponta), cor, vazio=True)
            _rotulo(ax, nome, ponta, f(ponta), abaixo=f(ponta) > 0)

        # Ponta fora da tela (Falsa Posição com zoom): seta na borda dizendo onde ela está
        for ponta, nome, parado, esquerda in ((a, "a", passo["parado_a"], True),
                                              (b, "b", passo["parado_b"], False)):
            if (ponta < janela[0]) if esquerda else (ponta > janela[1]):
                texto_ponta = f"{nome} = {ponta:.6g}"
                if parado >= 2:
                    texto_ponta += f"  (parado há {parado} iterações)"
                ax.annotate(f"← {texto_ponta}" if esquerda else f"{texto_ponta} →",
                            xy=(0.015 if esquerda else 0.985, 0.95), xycoords="axes fraction",
                            ha="left" if esquerda else "right", va="top", color=cor,
                            fontsize=10, fontweight="bold")

        if metodo == "Falsa Posição":
            _reta(ax, (a, f(a)), (b, f(b)), janela, cor, alpha)
            if fase == "desenho":  # o ponto desce pela corda até cruzar o eixo
                origem = b if abs(b - x) < abs(a - x) else a
                _caminhar(ax, (origem, f(origem)), (x, 0.0), _suave(t), cor)
        elif fase == "desenho":  # Bissecção: dois pontos saem de a e b e se encontram no meio
            s = _suave(t)
            for ponta in (a, b):
                _ponto(ax, ponta + (x - ponta) * s, 0, cor, tamanho=6)
        texto = f"[a, b] = [{passo['a']:.10g}, {passo['b']:.10g}]"
        if metodo == "Bissecção":
            texto += f"     x{_sub(k)} = (a + b) / 2"

    elif metodo == "Newton-Raphson":
        p = passo["pontos"][0]
        fp = f(p)
        ax.plot([p, p], [0, fp], color=cor, linewidth=1, linestyle=":")
        _ponto(ax, p, fp, cor, vazio=True)
        _rotulo(ax, f"x{_sub(k - 1)}", p, fp)
        _reta(ax, (p, fp), (x, 0.0), janela, cor, alpha)  # tangente: passa por (p, f(p)) e (xₖ, 0)
        if fase == "desenho":  # desce pela tangente até o eixo
            _caminhar(ax, (p, fp), (x, 0.0), _suave(t), cor)
        texto = f"tangente em x{_sub(k - 1)} = {p:.10g}"

    else:  # Secante
        p0, p1 = passo["pontos"]
        for i, p in enumerate((p0, p1)):
            _ponto(ax, p, f(p), cor, vazio=True)
            _rotulo(ax, f"x{_sub(k - 2 + i)}", p, f(p))
        _reta(ax, (p0, f(p0)), (p1, f(p1)), janela, cor, alpha)
        if fase == "desenho":  # segue a secante até o eixo
            _caminhar(ax, (p1, f(p1)), (x, 0.0), _suave(t), cor)
        texto = f"secante por x{_sub(k - 2)} e x{_sub(k - 1)}"

    if fase == "pausa":
        # A linha até f(xₖ) cresce na primeira metade da pausa
        s = _suave(min(1.0, 2 * t))
        ax.plot([x, x], [0, fx * s], color=cor, linewidth=1.2, linestyle=":")
        if s == 1.0:
            _ponto(ax, x, fx, cor, tamanho=5)
        _ponto(ax, x, 0, COR_RAIZ, tamanho=9)
        _rotulo(ax, f"x{_sub(k)}", x, 0, cor=COR_RAIZ, abaixo=fx > 0, fontweight="bold")
        texto += f"\nx{_sub(k)} = {x:.10f}     f(x{_sub(k)}) = {fx:.3e}"
    else:
        texto += "\n"
    return texto


def _desenhar_visao_geral(ax, f, caso: dict, passos: list[dict], k: int,
                          janela, cor: str) -> None:
    """Mini-gráfico com o intervalo inteiro e, em vermelho, onde o zoom está."""
    inicial = _janela_inicial(caso)
    xs = np.linspace(inicial[0], inicial[1], 200)
    ys = [v if (v := _valor_seguro(f, x)) is not None else np.nan for x in xs]

    ax.set_facecolor(COR_FUNDO)
    ax.set_xticks([])
    ax.set_yticks([])
    for borda in ax.spines.values():
        borda.set_color(COR_TEXTO_SECUNDARIO)
    ax.axhline(0, color=COR_TEXTO_SECUNDARIO, linewidth=0.8)
    ax.plot(xs, ys, color=COR_TEXTO, linewidth=1.2)

    if k >= 1:
        a, b = passos[k - 1]["a"], passos[k - 1]["b"]
        ax.axvspan(a, b, color=cor, alpha=0.15, linewidth=0)
        ax.plot([a, b], [f(a), f(b)], color=cor, linewidth=1, linestyle="--")

    # Janela do zoom: faixa se ainda for visível, senão uma linha
    if (janela[1] - janela[0]) > (inicial[1] - inicial[0]) * 0.01:
        ax.axvspan(*janela, color=COR_RAIZ, alpha=0.25, linewidth=0)
    else:
        ax.axvline((janela[0] + janela[1]) / 2, color=COR_RAIZ, linewidth=1.5)
    ax.set_xlim(*inicial)
    ax.set_title("visão geral (vermelho = zoom)", loc="left", fontsize=8,
                 color=COR_TEXTO_SECUNDARIO)


def _desenhar_residuos(ax, f, passos: list[dict], k: int, fase: str,
                       eps: float, cor: str, escala: tuple) -> None:
    """|f(xₖ)| em escala log, só até a iteração atual."""
    n_max, limites_y = escala
    ate = k if fase == "pausa" else k - 1
    residuos = [max(abs(f(p["x"])), 1e-17) for p in passos]

    ax.axhline(eps, color=COR_TEXTO_SECUNDARIO, linestyle="--", linewidth=1)
    ax.annotate(f"ε = {eps:g}", (0.6, eps), textcoords="offset points", xytext=(0, 4),
                color=COR_TEXTO_SECUNDARIO, fontsize=9)
    if ate >= 1:
        iteracoes = range(1, ate + 1)
        ax.plot(iteracoes, residuos[:ate], color=cor, linewidth=2, marker="o",
                markersize=5, markeredgecolor=COR_FUNDO)
        ax.plot(ate, residuos[ate - 1], marker="o", markersize=9, color=COR_RAIZ,
                markeredgecolor=COR_FUNDO, markeredgewidth=2, zorder=5)

    ax.set_yscale("log")
    ax.set_xlim(0.5, n_max + 0.5)
    ax.set_ylim(*limites_y)
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.set_title("|f(xₖ)| por iteração", loc="left", color=COR_TEXTO, fontsize=11)
    ax.set_xlabel("iteração k", color=COR_TEXTO_SECUNDARIO)


# ---------------------------------------------------------------------------
# Animação de um método
# ---------------------------------------------------------------------------

def escala_comum(f: Callable[[float], float], resultados: list[Resultado],
                 eps: float) -> tuple:
    """
    Eixos do gráfico |f(xₖ)| iguais para todos os métodos, para os vídeos
    poderem ser comparados: devolve (maior número de iterações, limites do eixo y).
    """
    residuos = []
    for r in resultados:
        for x in r.historico:
            valor = _valor_seguro(f, x)
            if valor is not None and math.isfinite(valor):
                residuos.append(max(abs(valor), 1e-17))
    residuos = residuos or [1.0]
    n_max = max((len(r.historico) for r in resultados), default=1)
    return n_max, (min(min(residuos), eps) / 10, max(max(residuos), eps) * 10)


def _quadros_em_tempo_real(total: int):
    """
    Gerador de índices de quadro guiado pelo RELÓGIO, não pela contagem.

    Ao vivo, cada quadro leva ~130 ms para ser desenhado (bem mais que os
    33 ms de 30 fps). Se a animação mostrasse todos os quadros, ficaria em
    câmera lenta. Aqui, a cada vez que o matplotlib pede um quadro, damos o
    quadro que "deveria" estar na tela agora — pulando os que não deu tempo
    de desenhar. A animação fica menos fluida, mas com a duração certa.
    """
    inicio = time.perf_counter()
    while True:
        i = int((time.perf_counter() - inicio) * FPS)
        if i >= total:  # chegou ao fim: recomeça (repetição)
            inicio = time.perf_counter()
            i = 0
        yield i


def criar_animacao(f: Callable[[float], float], resultado: Resultado, caso: dict,
                   eps: float, nome_var: str = "x", escala: tuple | None = None,
                   tempo_real: bool = False):
    """
    Monta a figura e a animação das iterações de UM método.
    escala: eixos do gráfico |f(xₖ)| (ver escala_comum); sem ela, usa só este método.
    tempo_real: True para exibir ao vivo pulando quadros (duração certa);
                False para salvar em vídeo (precisa de todos os quadros).
    """
    metodo = resultado.metodo
    cor = CORES_METODOS.get(metodo, COR_TEXTO)
    passos = montar_passos(f, resultado, caso)
    quadros = _roteiro(passos, caso)
    escala = escala or escala_comum(f, [resultado], eps)

    fig = plt.figure(figsize=(12, 6.2), facecolor=COR_FUNDO)
    grade = fig.add_gridspec(1, 2, width_ratios=[1.7, 1], wspace=0.22,
                             top=0.76, bottom=0.10, left=0.07, right=0.97)
    ax_f = fig.add_subplot(grade[0, 0])
    ax_r = fig.add_subplot(grade[0, 1])

    # Falsa Posição: o zoom segue só a ponta que anda, então um mini-gráfico
    # mostra o intervalo inteiro para não perder a referência
    ax_geral = None
    if metodo == "Falsa Posição":
        pos = ax_f.get_position()
        ax_geral = fig.add_axes([pos.x0 + pos.width * 0.66, pos.y0 + pos.height * 0.05,
                                 pos.width * 0.32, pos.height * 0.32])

    fig.text(0.07, 0.95, f"{caso['nome']} — {metodo}", fontsize=15,
             fontweight="bold", color=COR_TEXTO)
    fig.text(0.07, 0.912, f"f({nome_var}) = {caso['funcao']}   ·   ε = {eps:g}",
             fontsize=10, color=COR_TEXTO_SECUNDARIO)
    titulo_iter = fig.text(0.97, 0.912, "", ha="right", fontsize=13,
                           fontweight="bold", color=cor)
    info = fig.text(0.07, 0.885, "", va="top", fontsize=10, color=COR_TEXTO,
                    family="monospace")

    largura_inicial = _janela_inicial(caso)[1] - _janela_inicial(caso)[0]

    def desenhar(i):
        k, janela, fase, t = quadros[i]
        ultimo = passos and i >= len(quadros) - QUADROS_FINAL
        ax_f.cla()
        ax_r.cla()
        _estilizar(ax_f)
        _estilizar(ax_r)

        info.set_text(_desenhar_geometria(ax_f, f, metodo, passos, k, fase, t,
                                          janela, caso, cor))
        _desenhar_residuos(ax_r, f, passos, k, fase, eps, cor, escala)
        if ax_geral is not None:
            ax_geral.cla()
            _desenhar_visao_geral(ax_geral, f, caso, passos, k, janela, cor)

        zoom = largura_inicial / (janela[1] - janela[0])
        ax_f.set_title(f"f({nome_var})" + (f"   (zoom ×{zoom:,.0f})".replace(",", " ")
                                           if zoom >= 1.5 else ""),
                       loc="left", color=COR_TEXTO, fontsize=11)
        ax_f.set_xlabel(nome_var, color=COR_TEXTO_SECUNDARIO)

        if ultimo:
            if resultado.convergiu:
                titulo_iter.set_text(f"✔ raiz ≈ {resultado.raiz:.10f} em {len(passos)} iterações")
            else:
                titulo_iter.set_text(f"✘ {resultado.erro}")
        else:
            titulo_iter.set_text(f"iteração {k} de {len(passos)}" if k else "início")

    if tempo_real:
        animacao = FuncAnimation(fig, desenhar,
                                 frames=lambda: _quadros_em_tempo_real(len(quadros)),
                                 interval=1, repeat=False, cache_frame_data=False)
    else:
        animacao = FuncAnimation(fig, desenhar, frames=len(quadros),
                                 interval=1000 / FPS, repeat=True)
    return fig, animacao


# ---------------------------------------------------------------------------
# Rodar os 4 métodos e animar
# ---------------------------------------------------------------------------

def _nome_variavel(texto: str) -> str:
    """Letra usada como variável na função (ex.: 't' em '5*(1 - exp(-t))')."""
    nomes = set(re.findall(r"[A-Za-z_]\w*", texto))
    nomes -= {"e", "exp", "sin", "sen", "cos", "tan", "log", "ln", "sqrt", "pi", "E"}
    return nomes.pop() if len(nomes) == 1 else "x"


PASTA_VIDEOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "animacoes")


def _prefixo(caso: dict) -> str | None:
    """
    Começo do nome dos arquivos: 'problema2', 'problema1' ou 'exemplo'.
    None para uma função digitada pelo usuário (não tem vídeo pronto).
    """
    if not any(caso["funcao"] == pronto["funcao"] for pronto in CASOS):
        return None
    achou = re.match(r"Problema (\d+)", caso["nome"])
    return f"problema{achou.group(1)}" if achou else "exemplo"


def _nome_arquivo(metodo: str) -> str:
    """'Falsa Posição' -> 'falsa_posicao' (sem espaço, hífen ou acento)."""
    return (metodo.lower().replace(" ", "_").replace("-", "_")
            .replace("ç", "c").replace("ã", "a"))


def _video_pronto(caso: dict, metodo: str, eps: float, max_iter: int) -> str | None:
    """
    Caminho do vídeo MP4 já gerado para este caso e método, se existir.
    Os vídeos foram gerados com eps e max_iter padrão: com outros valores
    as iterações mudam, então o vídeo não vale e a animação roda ao vivo.
    """
    prefixo = _prefixo(caso)
    if prefixo is None or eps != EPS_PADRAO or max_iter != MAX_ITER_PADRAO:
        return None
    caminho = os.path.join(PASTA_VIDEOS, f"{prefixo}_{_nome_arquivo(metodo)}.mp4")
    return caminho if os.path.exists(caminho) else None


def _abrir_video(caminho: str) -> None:
    """Abre o vídeo no player padrão do sistema (roda liso, a 30 fps)."""
    if sys.platform == "win32":
        os.startfile(caminho)  # só existe no Windows
    else:
        webbrowser.open("file://" + caminho)


def rodar_metodos(caso: dict, eps: float, max_iter: int):
    """Roda os 4 métodos do caso e devolve (f, resultados)."""
    f, df, _ = ler_funcao(caso["funcao"])
    a, b = caso["a"], caso["b"]
    resultados = [
        bisseccao(f, a, b, eps, max_iter),
        falsa_posicao(f, a, b, eps, max_iter),
        newton_raphson(f, df, caso["x0_newton"], eps, max_iter, (a, b)),
        secante(f, caso["x0_secante"], caso["x1_secante"], eps, max_iter, (a, b)),
    ]
    return f, resultados


def mostrar_animacoes(f, resultados: list[Resultado], caso: dict, eps: float,
                      max_iter: int = MAX_ITER_PADRAO, nome_var: str | None = None) -> None:
    """
    Abre um seletor com 4 quadrados, um por método. Clicar num quadrado:
      - toca o vídeo MP4 pronto (casos de casos.py), liso a 30 fps; ou
      - abre a animação ao vivo (funções digitadas), com a duração certa.
    O seletor continua aberto para escolher outro método; feche-o para voltar ao menu.
    """
    nome_var = nome_var or _nome_variavel(caso["funcao"])
    escala = escala_comum(f, resultados, eps)
    abertas = []  # guarda as animações ao vivo (se não guardar, o Python as apaga)

    fig = plt.figure(figsize=(11, 3.6), facecolor=COR_FUNDO)
    fig.canvas.manager.set_window_title("Animações — escolha um método")
    fig.text(0.03, 0.90, "Clique num método para ver a animação das iterações",
             fontsize=13, fontweight="bold", color=COR_TEXTO)
    fig.text(0.03, 0.82, caso["nome"], fontsize=10, color=COR_TEXTO_SECUNDARIO)

    quadrados = {}  # área do quadrado (ax) -> resultado daquele método
    for i, r in enumerate(resultados):
        ax = fig.add_axes([0.03 + i * 0.2425, 0.08, 0.215, 0.62])
        ax.set_xticks([])
        ax.set_yticks([])
        cor = CORES_METODOS.get(r.metodo, COR_TEXTO)
        tem_animacao = bool(r.historico)
        ax.set_facecolor("#ffffff" if tem_animacao else COR_GRADE)
        for borda in ax.spines.values():
            borda.set_color(cor if tem_animacao else COR_TEXTO_SECUNDARIO)
            borda.set_linewidth(3)
        ax.axhspan(0.82, 1.0, color=cor if tem_animacao else COR_TEXTO_SECUNDARIO)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        ax.text(0.5, 0.58, r.metodo, ha="center", fontsize=12, fontweight="bold",
                color=COR_TEXTO)
        if tem_animacao:
            ax.text(0.5, 0.40, f"{len(r.historico)} iterações", ha="center",
                    fontsize=10, color=COR_TEXTO_SECUNDARIO)
            modo = ("▶ vídeo (30 fps)" if _video_pronto(caso, r.metodo, eps, max_iter)
                    else "▶ ao vivo")
            ax.text(0.5, 0.15, modo, ha="center", fontsize=10, color=COR_TEXTO)
            quadrados[ax] = r
        else:
            ax.text(0.5, 0.30, "sem iterações\npara animar", ha="center",
                    fontsize=9, color=COR_TEXTO_SECUNDARIO)

    def ao_clicar(evento):
        r = quadrados.get(evento.inaxes)  # em qual quadrado foi o clique?
        if r is None:
            return
        video = _video_pronto(caso, r.metodo, eps, max_iter)
        if video:
            print(f"  Abrindo vídeo: {os.path.basename(video)}")
            _abrir_video(video)
        else:
            print(f"  Animação ao vivo: {r.metodo}")
            fig_anim, animacao = criar_animacao(f, r, caso, eps, nome_var, escala,
                                                tempo_real=True)
            fig_anim.canvas.manager.set_window_title(f"Iterações — {r.metodo}")
            abertas.append(animacao)
            fig_anim.show()

    def ao_passar_mouse(evento):
        # Cursor de "mãozinha" em cima dos quadrados clicáveis
        clicavel = evento.inaxes in quadrados
        fig.canvas.set_cursor(Cursors.HAND if clicavel else Cursors.POINTER)

    fig.canvas.mpl_connect("button_press_event", ao_clicar)
    fig.canvas.mpl_connect("motion_notify_event", ao_passar_mouse)
    print("  Feche a janela de seleção (e as animações) para voltar ao menu.")
    plt.show()
    plt.close("all")


def salvar_animacoes(f, resultados: list[Resultado], caso: dict, eps: float,
                     pasta: str, prefixo: str, formato: str = "mp4",
                     metodo: str | None = None) -> None:
    """Salva um vídeo (mp4) ou GIF por método na pasta indicada."""
    os.makedirs(pasta, exist_ok=True)
    nome_var = _nome_variavel(caso["funcao"])
    escala = escala_comum(f, resultados, eps)  # mesma escala mesmo salvando um só método
    for r in resultados:
        if not r.historico:
            continue
        if metodo and metodo.lower() not in r.metodo.lower():
            continue
        fig, animacao = criar_animacao(f, r, caso, eps, nome_var, escala)
        caminho = os.path.join(pasta, f"{prefixo}_{_nome_arquivo(r.metodo)}.{formato}")
        if formato == "mp4":
            # yuv420p: formato de cor que abre em qualquer player e no PowerPoint
            escritor = FFMpegWriter(fps=FPS, codec="libx264",
                                    extra_args=["-pix_fmt", "yuv420p", "-crf", "18"])
            animacao.save(caminho, writer=escritor, dpi=160)
        else:
            animacao.save(caminho, writer=PillowWriter(fps=FPS), dpi=80)
        plt.close(fig)
        print(f"  salvo: {caminho}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Animação das iterações de cada método.")
    parser.add_argument("caso", nargs="?", type=int, default=3,
                        help="número do caso em casos.py (padrão: 3 = Problema 2, circuito RC)")
    parser.add_argument("--salvar", action="store_true",
                        help="salva vídeos MP4 em docs/animacoes/ em vez de abrir janelas")
    parser.add_argument("--gif", action="store_true",
                        help="salva GIFs em docs/animacoes/ em vez de abrir janelas")
    parser.add_argument("--metodo", help='salva só um método (ex.: --metodo "falsa")')
    args = parser.parse_args()

    caso = CASOS[args.caso - 1]
    f, resultados = rodar_metodos(caso, EPS_PADRAO, MAX_ITER_PADRAO)
    print(f">>> {caso['nome']}")
    if args.salvar or args.gif:
        salvar_animacoes(f, resultados, caso, EPS_PADRAO, os.path.join("docs", "animacoes"),
                         _prefixo(caso), "gif" if args.gif else "mp4", args.metodo)
    else:
        mostrar_animacoes(f, resultados, caso, EPS_PADRAO)


if __name__ == "__main__":
    main()
