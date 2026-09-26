"""
PARTE 1 — Métodos de intervalo: Bissecção e Falsa Posição.

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
              eps: float, max_iter: int) -> Resultado:
    """
    Encontra uma raiz de f em [a, b] pelo método da Bissecção.

    Passos:
      1. Verificar se f(a) * f(b) < 0. Se não, devolver Resultado com
         erro="Não há mudança de sinal em [a, b]".
      2. Marcar o tempo inicial com time.perf_counter().
      3. Repetir até max_iter vezes:
           - x = (a + b) / 2
           - guardar x em historico
           - se o critério de parada for atingido, parar
           - se f(a) * f(x) < 0, a raiz está em [a, x]  ->  b = x
             senão, a raiz está em [x, b]               ->  a = x
      4. Calcular tempo_ms = (fim - inicio) * 1000.
      5. Se chegou em max_iter sem parar, preencher erro avisando.
      6. Devolver Resultado("Bissecção", raiz, iteracoes, tempo_ms,
         abs(f(raiz)), erro, historico).
    """
    # TODO (Parte 1): implementar
    return Resultado("Bissecção", erro="Ainda não implementado")


def falsa_posicao(f: Callable[[float], float], a: float, b: float,
                  eps: float, max_iter: int) -> Resultado:
    """
    Encontra uma raiz de f em [a, b] pelo método da Falsa Posição.

    Igual à Bissecção, mas em vez do ponto médio usa o ponto onde a reta
    entre (a, f(a)) e (b, f(b)) cruza o eixo x:

        x = (a * f(b) - b * f(a)) / (f(b) - f(a))

    Atenção: se f(b) - f(a) == 0, há divisão por zero -> devolver erro.
    """
    # TODO (Parte 1): implementar
    return Resultado("Falsa Posição", erro="Ainda não implementado")
