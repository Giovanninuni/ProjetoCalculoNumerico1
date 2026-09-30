"""
Parte 2 - Métodos Abertos: Newton-Raphson e Secante.
Autoria: Tãua Oliveira

Regras comuns (ver PDF da Parte 2):
    - eps e max_iter são sempre os mesmos nos 4 métodos, para a
      comparação ser justa.
    - Critério de parada: |f(x)| < eps (a precisão que o PDF confere).
    - Cada função conta as iterações, guarda o histórico de x (um valor
      por iteração, sem os chutes iniciais) e mede o tempo com
      time.perf_counter().
    - Se x sair do intervalo informado, NÃO é falha: o método continua e
      o Resultado recebe um aviso (o PDF pede para registrar
      "extrapolação do intervalo").
    - Nunca usar print/input aqui — quem mostra os resultados na tela é
      o relatorio.py. Sempre devolver um Resultado (ver resultado.py).
"""

import time
from typing import Callable

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


def _montar_aviso(primeira_saida: str | None, raiz: float,
                  intervalo: tuple[float, float] | None) -> str | None:
    """Junta os avisos de extrapolação do intervalo (ou None se não houve)."""
    avisos = []
    if primeira_saida is not None:
        avisos.append(primeira_saida)
    if _fora_do_intervalo(raiz, intervalo):
        avisos.append(f"a raiz final está fora do intervalo {intervalo}")
    return "; ".join(avisos) if avisos else None


def newton_raphson(f: Callable[[float], float], df: Callable[[float], float],
                   x0: float, eps: float, max_iter: int,
                   intervalo: tuple[float, float] | None = None) -> Resultado:
    """Método de Newton-Raphson.

    Fórmula de cada iteração: x_novo = x - f(x) / f'(x)

    df já chega pronta (a derivada f'(x)) — não precisamos calculá-la
    aqui. Usa a reta tangente à curva no ponto atual para "pular" para
    perto da raiz.
    """
    inicio = time.perf_counter()
    historico = []
    primeira_saida = None  # guarda quando x saiu do intervalo pela 1ª vez
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

        # Extrapolação do intervalo: registra, mas deixa o método continuar
        if primeira_saida is None and _fora_do_intervalo(x_novo, intervalo):
            primeira_saida = f"saiu do intervalo na iteração {i} (x = {x_novo:.4f})"

        historico.append(x_novo)
        residuo = abs(f(x_novo))

        # Critério de parada: resíduo |f(x)| menor que eps
        if residuo < eps:
            return Resultado(
                metodo="Newton-Raphson",
                raiz=x_novo,
                iteracoes=i,
                tempo_ms=(time.perf_counter() - inicio) * 1000,
                residuo=residuo,
                aviso=_montar_aviso(primeira_saida, x_novo, intervalo),
                historico=historico,
            )

        x = x_novo

    # Não convergiu: devolve a última aproximação para aparecer na tabela
    return Resultado(
        metodo="Newton-Raphson",
        raiz=x,
        iteracoes=max_iter,
        tempo_ms=(time.perf_counter() - inicio) * 1000,
        residuo=abs(f(x)),
        erro=f"Não convergiu em {max_iter} iterações",
        aviso=primeira_saida,
        historico=historico,
    )


def secante(f: Callable[[float], float], x0: float, x1: float,
            eps: float, max_iter: int,
            intervalo: tuple[float, float] | None = None) -> Resultado:
    """Método da Secante.

    Fórmula de cada iteração:
        x_novo = x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))

    Depois de cada passo: x0 = x1 e x1 = x_novo.
    É como o Newton, mas troca a derivada pela inclinação da reta entre
    os dois últimos pontos.
    """
    inicio = time.perf_counter()
    historico = []
    primeira_saida = None  # guarda quando x saiu do intervalo pela 1ª vez

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

        # Extrapolação do intervalo: registra, mas deixa o método continuar
        if primeira_saida is None and _fora_do_intervalo(x_novo, intervalo):
            primeira_saida = f"saiu do intervalo na iteração {i} (x = {x_novo:.4f})"

        historico.append(x_novo)
        residuo = abs(f(x_novo))

        # Critério de parada: resíduo |f(x)| menor que eps
        if residuo < eps:
            return Resultado(
                metodo="Secante",
                raiz=x_novo,
                iteracoes=i,
                tempo_ms=(time.perf_counter() - inicio) * 1000,
                residuo=residuo,
                aviso=_montar_aviso(primeira_saida, x_novo, intervalo),
                historico=historico,
            )

        x0, x1 = x1, x_novo

    # Não convergiu: devolve a última aproximação para aparecer na tabela
    return Resultado(
        metodo="Secante",
        raiz=x1,
        iteracoes=max_iter,
        tempo_ms=(time.perf_counter() - inicio) * 1000,
        residuo=abs(f(x1)),
        erro=f"Não convergiu em {max_iter} iterações",
        aviso=primeira_saida,
        historico=historico,
    )
