"""
PARTE 3 — Saída: tabela comparativa e gráficos.

Só depende do formato Resultado (resultado.py), então pode ser feito e
testado antes dos métodos estarem prontos, usando resultados "falsos".
"""

from typing import Callable

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
    # TODO (Parte 3): implementar
    raise NotImplementedError


def plotar_grafico(f: Callable[[float], float], a: float, b: float,
                   resultados: list[Resultado], titulo: str = "") -> None:
    """
    (Bônus do PDF) Gráfico da função e das raízes encontradas.

    Sugestão com matplotlib:
      - Gráfico 1: curva de f em [a, b], eixo y = 0, e um marcador
        (cor diferente) na raiz de cada método que convergiu.
      - Gráfico 2: convergência — no eixo x a iteração, no eixo y
        |f(x_k)| em escala log, uma linha por método (usa .historico).
        Esse gráfico mostra visualmente que Newton/Secante descem muito
        mais rápido que Bissecção/Falsa Posição.
    """
    # TODO (Parte 3): implementar
    raise NotImplementedError
