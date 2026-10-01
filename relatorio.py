"""
PARTE 3 — Saída: tabela no terminal e janela com tabela e gráficos.

Só depende do formato Resultado (resultado.py): não sabe nada de como
cada método calcula, só lê os campos do resultado.
"""

from typing import Callable

import matplotlib.pyplot as plt
import numpy as np

from resultado import Resultado


def imprimir_tabela(resultados: list[Resultado]) -> None:
    """
    Mostra no terminal uma tabela com uma linha por método:

        Método          | Raiz         | Iterações | Tempo (ms) | |f(raiz)|
        ----------------+--------------+-----------+------------+----------
        Bissecção       | 0.7390851...  |        20 |     0.0123 | 4.1e-07
        ...

    Se resultado.erro não for None, mostrar a mensagem de erro na linha
    no lugar dos números (ex.: "FALHOU: derivada nula").
    Dica: f-strings com alinhamento, ex.: f"{texto:<15}" e f"{num:>10.6f}".
    """
    cabecalho = (f"{'Método':<15} | {'Raiz':>14} | {'Iterações':>9} | "
                 f"{'Tempo (ms)':>10} | {'|f(raiz)|':>9}")

    print()
    print(cabecalho)
    print("-" * len(cabecalho))  # linha de traços do mesmo tamanho do cabeçalho

    for r in resultados:
        if r.erro is not None:
            # O método falhou: mostra a mensagem no lugar dos números
            print(f"{r.metodo:<15} | {r.erro}")
        else:
            marca = " *" if r.aviso else ""  # * indica que há um aviso abaixo
            print(f"{r.metodo:<15} | {r.raiz:>14.10f} | {r.iteracoes:>9} | "
                  f"{r.tempo_ms:>10.4f} | {r.residuo:>9.2e}{marca}")

    # Avisos ficam abaixo da tabela para não desalinhar as colunas
    for r in resultados:
        if r.aviso:
            print(f"  * {r.metodo}: {r.aviso}")

    print()


# ---------------------------------------------------------------------------
# Janela com tabela e gráficos (bônus do PDF)
# ---------------------------------------------------------------------------

# Cada método tem sempre a mesma cor (paleta testada para daltonismo)
CORES_METODOS = {
    "Bissecção": "#2a78d6",       # azul
    "Falsa Posição": "#eb6834",   # laranja
    "Newton-Raphson": "#1baf7a",  # verde-água
    "Secante": "#eda100",         # amarelo
}
COR_TEXTO = "#0b0b0b"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_GRADE = "#e5e4e0"
COR_FUNDO = "#fcfcfb"
COR_RAIZ = "#e34948"


def _valor_seguro(f: Callable[[float], float], x: float) -> float | None:
    """Calcula f(x) sem quebrar: devolve None se der erro matemático."""
    try:
        return f(x)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


def _desenhar_tabela(ax, resultados: list[Resultado]) -> list[str]:
    """Desenha a tabela comparativa e devolve as notas (erros/avisos) para o rodapé."""
    ax.axis("off")  # a tabela não precisa de eixos

    colunas = ["", "Método", "Raiz", "Iterações", "Tempo (ms)", "|f(raiz)|", "Situação"]
    linhas = []
    notas = []

    for r in resultados:
        if r.erro is not None:
            situacao = "Falhou"
            notas.append(f"{r.metodo}: {r.erro}")
        elif r.aviso:
            situacao = "Convergiu *"
            notas.append(f"* {r.metodo}: {r.aviso}")
        else:
            situacao = "Convergiu"

        raiz = f"{r.raiz:.10f}" if r.raiz is not None else "—"
        residuo = f"{r.residuo:.2e}" if r.residuo is not None else "—"
        linhas.append(["", r.metodo, raiz, str(r.iteracoes),
                       f"{r.tempo_ms:.4f}", residuo, situacao])

    tabela = ax.table(cellText=linhas, colLabels=colunas, loc="center", cellLoc="center",
                      colWidths=[0.02, 0.17, 0.17, 0.10, 0.12, 0.12, 0.14])
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.scale(1, 1.6)  # linhas um pouco mais altas

    # Estilo: cabeçalho em negrito, bordas claras e um quadradinho com a cor do método
    for (linha, coluna), celula in tabela.get_celld().items():
        celula.set_edgecolor(COR_GRADE)
        celula.get_text().set_color(COR_TEXTO)
        if linha == 0:
            celula.get_text().set_weight("bold")
            celula.set_facecolor("#f0efec")
        elif coluna == 0:
            metodo = resultados[linha - 1].metodo
            celula.set_facecolor(CORES_METODOS.get(metodo, COR_GRADE))

    return notas


def _desenhar_funcao(ax, f: Callable[[float], float], a: float, b: float,
                     resultados: list[Resultado], nome_var: str) -> None:
    """Gráfico 1: a curva de f em [a, b] com as raízes encontradas marcadas."""
    # Agrupa os métodos que acharam a mesma raiz (um método aberto pode achar
    # OUTRA raiz da função, fora do intervalo — por isso não se tira média)
    # Duas raízes contam como a mesma se estiverem mais perto que 0,01% do intervalo
    tolerancia = (b - a) * 1e-4
    grupos = {}  # raiz -> lista de nomes de métodos que a encontraram
    for r in resultados:
        if not r.convergiu:
            continue
        for raiz_do_grupo in grupos:
            if abs(r.raiz - raiz_do_grupo) < tolerancia:
                grupos[raiz_do_grupo].append(r.metodo)
                break
        else:  # o for terminou sem break: é uma raiz nova
            grupos[r.raiz] = [r.metodo]

    # O gráfico cobre [a, b] e também qualquer raiz que tenha caído fora dele
    inicio = min([a] + list(grupos))
    fim = max([b] + list(grupos))
    margem = (fim - inicio) * 0.05
    xs = np.linspace(inicio - margem, fim + margem, 400)  # 400 pontos igualmente espaçados
    ys = []
    for x in xs:
        y = _valor_seguro(f, x)
        ys.append(y if y is not None else np.nan)  # nan = "buraco" no gráfico

    ax.axvspan(a, b, color=COR_GRADE, alpha=0.5, linewidth=0)  # faixa do intervalo [a, b]
    ax.axhline(0, color=COR_TEXTO_SECUNDARIO, linewidth=1)     # linha y = 0
    ax.plot(xs, ys, color=COR_TEXTO, linewidth=2)

    # Uma marca por raiz diferente, com os métodos que a encontraram
    for i, (raiz, metodos) in enumerate(sorted(grupos.items())):
        ax.plot(raiz, 0, marker="o", markersize=9, color=COR_RAIZ,
                markeredgecolor=COR_FUNDO, markeredgewidth=2, zorder=5)
        deslocamento = 10 + 28 * (i % 2)  # alterna a altura se houver várias raízes
        ax.annotate(f"raiz ≈ {raiz:.6f}\n({', '.join(metodos)})", (raiz, 0),
                    textcoords="offset points", xytext=(6, deslocamento),
                    color=COR_TEXTO, fontsize=9)

    ax.set_title(f"f({nome_var}) no intervalo [{a:g}, {b:g}]", loc="left",
                 color=COR_TEXTO, fontsize=11)
    ax.set_xlabel(nome_var, color=COR_TEXTO_SECUNDARIO)
    ax.set_ylabel(f"f({nome_var})", color=COR_TEXTO_SECUNDARIO)
    ax.grid(color=COR_GRADE, linewidth=0.8)


def _desenhar_convergencia(ax, f: Callable[[float], float],
                           resultados: list[Resultado], eps: float) -> None:
    """Gráfico 2: |f(x_k)| a cada iteração, em escala log, uma linha por método."""
    for r in resultados:
        if not r.historico:
            continue
        iteracoes = range(1, len(r.historico) + 1)
        residuos = []
        for x in r.historico:
            valor = _valor_seguro(f, x)
            if valor is None:
                residuos.append(np.nan)
            else:
                # log(0) não existe: resíduo exatamente 0 vira um valor bem pequeno
                residuos.append(max(abs(valor), 1e-17))

        cor = CORES_METODOS.get(r.metodo, COR_TEXTO)
        ax.plot(iteracoes, residuos, color=cor, linewidth=2, marker="o", markersize=5,
                markeredgecolor=COR_FUNDO, label=r.metodo)
        # Rótulo direto no fim de cada linha, com o número de iterações
        ax.annotate(f" {r.metodo} ({len(r.historico)})", (len(r.historico), residuos[-1]),
                    color=COR_TEXTO_SECUNDARIO, fontsize=9, va="center")

    # Linha tracejada do eps: abaixo dela, o método parou
    ax.axhline(eps, color=COR_TEXTO_SECUNDARIO, linestyle="--", linewidth=1)
    ax.annotate(f"ε = {eps:g}", (1, eps), textcoords="offset points", xytext=(2, 4),
                color=COR_TEXTO_SECUNDARIO, fontsize=9)

    ax.set_yscale("log")
    ax.set_title("Convergência: |f(xₖ)| por iteração", loc="left", color=COR_TEXTO, fontsize=11)
    ax.set_xlabel("iteração k", color=COR_TEXTO_SECUNDARIO)
    ax.set_ylabel("|f(xₖ)|  (escala log)", color=COR_TEXTO_SECUNDARIO)
    ax.grid(color=COR_GRADE, linewidth=0.8)
    ax.legend(frameon=False, fontsize=9, loc="upper right")

    # Eixo x começa na iteração 1 e sobra espaço à direita para os rótulos
    maior = max((len(r.historico) for r in resultados), default=1)
    ax.set_xlim(0.5, maior * 1.3 + 1)


def criar_figura(f: Callable[[float], float], a: float, b: float,
                 resultados: list[Resultado], titulo: str, subtitulo: str,
                 eps: float, nome_var: str = "x"):
    """Monta a figura completa: tabela em cima, dois gráficos embaixo."""
    fig = plt.figure(figsize=(13, 8.5), facecolor=COR_FUNDO)
    grade = fig.add_gridspec(2, 2, height_ratios=[1, 1.6], hspace=0.35, wspace=0.25,
                             top=0.88, bottom=0.08, left=0.06, right=0.97)

    fig.suptitle(titulo, x=0.06, ha="left", fontsize=15, fontweight="bold", color=COR_TEXTO)
    fig.text(0.06, 0.915, subtitulo, fontsize=10, color=COR_TEXTO_SECUNDARIO)

    ax_tabela = fig.add_subplot(grade[0, :])  # linha de cima, ocupando as 2 colunas
    notas = _desenhar_tabela(ax_tabela, resultados)
    if notas:
        ax_tabela.text(0, -0.05, "\n".join(notas), transform=ax_tabela.transAxes,
                       fontsize=9, color=COR_TEXTO_SECUNDARIO, va="top")

    ax_funcao = fig.add_subplot(grade[1, 0])  # embaixo à esquerda
    ax_conv = fig.add_subplot(grade[1, 1])    # embaixo à direita
    for ax in (ax_funcao, ax_conv):
        ax.set_facecolor(COR_FUNDO)
        ax.tick_params(colors=COR_TEXTO_SECUNDARIO)
        for borda in ax.spines.values():
            borda.set_color(COR_GRADE)

    _desenhar_funcao(ax_funcao, f, a, b, resultados, nome_var)
    _desenhar_convergencia(ax_conv, f, resultados, eps)
    return fig


def mostrar_janela(f: Callable[[float], float], a: float, b: float,
                   resultados: list[Resultado], titulo: str, subtitulo: str,
                   eps: float, nome_var: str = "x") -> None:
    """Abre a janela e espera o usuário fechá-la para voltar ao menu."""
    fig = criar_figura(f, a, b, resultados, titulo, subtitulo, eps, nome_var)
    fig.canvas.manager.set_window_title("Simulador de Zeros — Resultados")
    plt.show()  # bloqueia até a janela ser fechada
    plt.close(fig)
