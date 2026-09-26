"""
PARTE 3 — Entrada de dados do usuário.

Responsável por transformar o que o usuário digita em algo que os
métodos consigam usar, e por não deixar o programa quebrar com entrada
inválida (o PDF avalia "facilidade na entrada dos dados").
"""

from typing import Callable


def ler_funcao(texto: str) -> tuple[Callable[[float], float], Callable[[float], float], str]:
    """
    Converte um texto como "cos(x) - x" em duas funções Python: f e f'.

    Ideia com sympy:
      1. expr = sympy.sympify(texto)          -> texto vira expressão
      2. descobrir a variável (x, t, ...) com expr.free_symbols
         (deve haver exatamente UMA variável; senão, erro)
      3. dexpr = sympy.diff(expr, variavel)   -> derivada automática
      4. f  = sympy.lambdify(variavel, expr,  "math")
         df = sympy.lambdify(variavel, dexpr, "math")
      5. devolver (f, df, str(dexpr)) — o texto da derivada serve para
         mostrar ao usuário qual f'(x) foi usada.

    Se o texto for inválido, lançar ValueError com mensagem amigável.
    """
    # TODO (Parte 3): implementar
    raise NotImplementedError


def ler_float(mensagem: str, padrao: float | None = None) -> float:
    """
    Pergunta um número ao usuário até ele digitar algo válido.

    - Aceitar vírgula como separador decimal ("0,5" -> 0.5).
    - Aceitar notação científica ("1e-6").
    - Se padrao não for None e o usuário só apertar Enter, usar o padrão.
    """
    # TODO (Parte 3): implementar
    raise NotImplementedError


def ler_int(mensagem: str, padrao: int | None = None) -> int:
    """Igual ao ler_float, mas para inteiros positivos (ex.: max_iter)."""
    # TODO (Parte 3): implementar
    raise NotImplementedError
