"""
PARTE 2 — Métodos abertos: Newton-Raphson e Secante.

Partem de uma ou duas estimativas iniciais (sem exigir mudança de sinal)
e usam retas tangentes/secantes para "pular" direto para perto da raiz.
Convergem bem mais rápido, mas podem falhar (derivada nula, divisão por
zero, divergir ou sair do intervalo de interesse).

Critério de parada combinado pela equipe (usar o MESMO nos 4 métodos):
    parar quando |f(x)| < eps   OU   |x_novo - x_anterior| < eps
"""

import time
from typing import Callable

from resultado import Resultado


def newton_raphson(f: Callable[[float], float], df: Callable[[float], float],
                   x0: float, eps: float, max_iter: int,
                   intervalo: tuple[float, float] | None = None) -> Resultado:
    """
    Encontra uma raiz de f a partir de x0 pelo método de Newton-Raphson.

    Fórmula de cada iteração (reta tangente em x):

        x_novo = x - f(x) / df(x)

    Passos:
      1. Marcar o tempo inicial com time.perf_counter().
      2. Repetir até max_iter vezes:
           - se df(x) == 0 (ou muito próximo de 0), devolver erro
             "Derivada nula em x = ..."
           - calcular x_novo e guardar em historico
           - se intervalo foi informado e x_novo saiu dele, registrar
             aviso de "extrapolação do intervalo" (a equipe decide se
             para ou só avisa)
           - verificar critério de parada
           - x = x_novo
      3. Calcular tempo_ms, montar e devolver o Resultado.
    """
    # TODO (Parte 2): implementar
    return Resultado("Newton-Raphson", erro="Ainda não implementado")


def secante(f: Callable[[float], float], x0: float, x1: float,
            eps: float, max_iter: int,
            intervalo: tuple[float, float] | None = None) -> Resultado:
    """
    Encontra uma raiz de f a partir de x0 e x1 pelo método da Secante.

    Parecido com Newton, mas troca a derivada pela inclinação da reta
    que passa pelos dois últimos pontos:

        x_novo = x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))

    Atenção: se f(x1) - f(x0) == 0, há divisão por zero -> devolver erro.
    Depois de cada iteração: x0 = x1 e x1 = x_novo.
    """
    # TODO (Parte 2): implementar
    return Resultado("Secante", erro="Ainda não implementado")
