"""
Parte 2 - Métodos Abertos: Newton-Raphson e Secante.

Regras comuns (ver PDF da Parte 2):
    - eps e max_iter são sempre os mesmos nos 4 métodos, para a
      comparação ser justa.
    - Critério de parada: |f(x)| < eps OU |x_novo - x_anterior| < eps.
    - Cada função conta as iterações, guarda o histórico de x e mede o
      tempo com time.perf_counter().
    - Nunca usar print/input aqui — quem mostra os resultados na tela é
      o relatorio.py. Sempre devolver um Resultado (ver resultado.py).
"""

import time

from resultado import Resultado

# Tolerância usada só para decidir se um denominador é "zero demais"
# para dividir (derivada nula no Newton, f(x1) == f(x0) na Secante).
# É bem menor que o eps de convergência para não confundir os dois usos.
_TOLERANCIA_DIVISAO = 1e-14


def _fora_do_intervalo(x: float, intervalo: tuple[float, float] | None) -> bool:
    """True se um intervalo foi informado e x caiu fora dele."""
    if intervalo is None:
        return False
    minimo, maximo = intervalo
    return x < minimo or x > maximo


def newton_raphson(f, df, x0, eps, max_iter, intervalo=None):
    """Método de Newton-Raphson.

    Fórmula de cada iteração: x_novo = x - f(x) / f'(x)

    df já chega pronta (a derivada f'(x)) — não precisamos calculá-la
    aqui. Usa a reta tangente à curva no ponto atual para "pular" para
    perto da raiz.
    """
    inicio = time.perf_counter()
    historico = [x0]
    x = x0

    for i in range(1, max_iter + 1):
        derivada = df(x)

        if abs(derivada) < _TOLERANCIA_DIVISAO:
            return Resultado(
                metodo="Newton-Raphson",
                iteracoes=i - 1,
                tempo_ms=(time.perf_counter() - inicio) * 1000,
                erro=f"Derivada nula (ou muito próxima de 0) em x = {x:.10f}",
                historico=historico,
            )

        x_novo = x - f(x) / derivada

        if _fora_do_intervalo(x_novo, intervalo):
            return Resultado(
                metodo="Newton-Raphson",
                iteracoes=i,
                tempo_ms=(time.perf_counter() - inicio) * 1000,
                erro=f"x_novo = {x_novo:.10f} saiu do intervalo informado {intervalo}",
                historico=historico,
            )

        historico.append(x_novo)
        residuo = abs(f(x_novo))

        if residuo < eps or abs(x_novo - x) < eps:
            return Resultado(
                metodo="Newton-Raphson",
                raiz=x_novo,
                iteracoes=i,
                tempo_ms=(time.perf_counter() - inicio) * 1000,
                residuo=residuo,
                historico=historico,
            )

        x = x_novo

    return Resultado(
        metodo="Newton-Raphson",
        iteracoes=max_iter,
        tempo_ms=(time.perf_counter() - inicio) * 1000,
        erro=f"Não convergiu em {max_iter} iterações",
        historico=historico,
    )


def secante(f, x0, x1, eps, max_iter, intervalo=None):
    """Método da Secante.

    Fórmula de cada iteração:
        x_novo = x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))

    Depois de cada passo: x0 = x1 e x1 = x_novo.
    É como o Newton, mas troca a derivada pela inclinação da reta entre
    os dois últimos pontos.
    """
    inicio = time.perf_counter()
    historico = [x0, x1]

    for i in range(1, max_iter + 1):
        fx0 = f(x0)
        fx1 = f(x1)

        if abs(fx1 - fx0) < _TOLERANCIA_DIVISAO:
            return Resultado(
                metodo="Secante",
                iteracoes=i - 1,
                tempo_ms=(time.perf_counter() - inicio) * 1000,
                erro=f"Divisão por zero: f(x1) == f(x0) (x0 = {x0:.10f}, x1 = {x1:.10f})",
                historico=historico,
            )

        x_novo = x1 - fx1 * (x1 - x0) / (fx1 - fx0)

        if _fora_do_intervalo(x_novo, intervalo):
            return Resultado(
                metodo="Secante",
                iteracoes=i,
                tempo_ms=(time.perf_counter() - inicio) * 1000,
                erro=f"x_novo = {x_novo:.10f} saiu do intervalo informado {intervalo}",
                historico=historico,
            )

        historico.append(x_novo)
        residuo = abs(f(x_novo))

        if residuo < eps or abs(x_novo - x1) < eps:
            return Resultado(
                metodo="Secante",
                raiz=x_novo,
                iteracoes=i,
                tempo_ms=(time.perf_counter() - inicio) * 1000,
                residuo=residuo,
                historico=historico,
            )

        x0, x1 = x1, x_novo

    return Resultado(
        metodo="Secante",
        iteracoes=max_iter,
        tempo_ms=(time.perf_counter() - inicio) * 1000,
        erro=f"Não convergiu em {max_iter} iterações",
        historico=historico,
    )
