"""
PARTE 1 — Métodos de intervalo: Bissecção e Falsa Posição.
Autor: Caio Benevides

Os dois partem de um intervalo [a, b] onde f(a) e f(b) têm sinais
opostos (Teorema de Bolzano) e vão encolhendo esse intervalo até
encontrar a raiz. Sempre convergem, mas costumam ser mais lentos.

Critério de parada combinado pela equipe (usar o MESMO nos 4 métodos):
    parar quando |f(x)| < eps   OU   |x_novo - x_anterior| < eps
"""

import time
from typing import Callable

from resultado import Resultado


def bisseccao(f: Callable[[float], float], a: float, b: float,
              eps: float = 1e-6, max_iter: int = 100) -> Resultado:
    """
    Encontra uma raiz de f em [a, b] pelo método da Bissecção.
    A cada iteração, x é o ponto médio do intervalo.
    """
    inicio_tempo = time.perf_counter()
    historico = []

    # Checagem de falha: sem mudança de sinal
    if f(a) * f(b) >= 0:
        return Resultado(metodo="Bissecção",
                         erro="Falha: Sem mudança de sinal no intervalo inicial.")

    x_anterior = None

    for iteracao in range(1, max_iter + 1):
        x = (a + b) / 2.0
        fx = f(x)
        historico.append(x)

        # Critério de parada
        if abs(fx) < eps or (x_anterior is not None and abs(x - x_anterior) < eps):
            return Resultado(
                metodo="Bissecção",
                raiz=x,
                iteracoes=iteracao,
                tempo_ms=(time.perf_counter() - inicio_tempo) * 1000,
                residuo=abs(fx),
                historico=historico
            )

        # Atualização do intervalo mantendo a raiz
        if f(a) * fx < 0:
            b = x
        else:
            a = x

        x_anterior = x

    # Não convergiu: devolve a última aproximação para aparecer na tabela
    return Resultado(
        metodo="Bissecção",
        raiz=x,
        iteracoes=max_iter,
        tempo_ms=(time.perf_counter() - inicio_tempo) * 1000,
        residuo=abs(fx),
        erro="Falha: Não convergiu após o número máximo de iterações.",
        historico=historico
    )


def falsa_posicao(f: Callable[[float], float], a: float, b: float,
                  eps: float = 1e-6, max_iter: int = 100) -> Resultado:
    """
    Encontra uma raiz de f em [a, b] pelo método da Falsa Posição.
    A cada iteração, x é onde a reta entre (a, f(a)) e (b, f(b)) cruza o eixo x.
    """
    inicio_tempo = time.perf_counter()
    historico = []

    # Checagem de falha: sem mudança de sinal
    if f(a) * f(b) >= 0:
        return Resultado(metodo="Falsa Posição",
                         erro="Falha: Sem mudança de sinal no intervalo inicial.")

    x_anterior = None

    for iteracao in range(1, max_iter + 1):
        fa = f(a)
        fb = f(b)

        # Checagem de falha: divisão por zero
        if fb - fa == 0:
            return Resultado(
                metodo="Falsa Posição",
                iteracoes=iteracao,
                tempo_ms=(time.perf_counter() - inicio_tempo) * 1000,
                erro="Falha: Divisão por zero (f(b) = f(a)).",
                historico=historico
            )

        x = (a * fb - b * fa) / (fb - fa)
        fx = f(x)
        historico.append(x)

        # Critério de parada
        if abs(fx) < eps or (x_anterior is not None and abs(x - x_anterior) < eps):
            return Resultado(
                metodo="Falsa Posição",
                raiz=x,
                iteracoes=iteracao,
                tempo_ms=(time.perf_counter() - inicio_tempo) * 1000,
                residuo=abs(fx),
                historico=historico
            )

        # Atualização do intervalo mantendo a raiz
        if fa * fx < 0:
            b = x
        else:
            a = x

        x_anterior = x

    # Não convergiu: devolve a última aproximação para aparecer na tabela
    return Resultado(
        metodo="Falsa Posição",
        raiz=x,
        iteracoes=max_iter,
        tempo_ms=(time.perf_counter() - inicio_tempo) * 1000,
        residuo=abs(fx),
        erro="Falha: Não convergiu após o número máximo de iterações.",
        historico=historico
    )
