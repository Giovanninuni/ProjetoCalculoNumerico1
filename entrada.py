"""
Entrada de dados: transforma o que o usuário digita em algo que os
métodos conseguem usar, sem deixar o programa quebrar com entrada inválida.
Responsável: Giovanni Éber

Dois tipos de função:
    ler_funcao       -> só CONVERTE um texto já pronto (vindo de casos.py
                        ou digitado); não faz input().
    ler_float,       -> CONVERSAM com o usuário: perguntam, validam e
    ler_int,            perguntam de novo até a resposta ser válida.
    montar_caso_personalizado
"""

import math
from typing import Callable

import sympy


def ler_funcao(texto: str) -> tuple[Callable[[float], float], Callable[[float], float], str]:
    """
    Converte um texto como "cos(x) - x" em duas funções Python: f e f'.

    Fluxo:
        texto -> sympify (vira expressão simbólica)
              -> confere que há exatamente UMA variável (x, t, ...)
              -> diff (derivada automática, usada pelo Newton)
              -> lambdify com "math" (vira função Python rápida)

    Devolve (f, df, texto da derivada). O texto da derivada é mostrado ao
    usuário para ele conferir qual f'(x) foi usada.
    Lança ValueError com mensagem amigável se o texto for inválido.
    """
    texto = texto.replace("^", "**")  # permite escrever potência com ^ (em Python é **)

    # Nomes que o sympy deve entender de um jeito especial
    nomes_especiais = {
        "e": sympy.E,      # e = número de Euler (2,718...), não uma variável
        "sen": sympy.sin,  # permite escrever seno em português
        "ln": sympy.log,   # ln = logaritmo natural
    }

    try:
        expr = sympy.sympify(texto, locals=nomes_especiais)  # transforma o texto em expressão
    except (sympy.SympifyError, TypeError):
        raise ValueError(f"Não entendi a função '{texto}'. Exemplo válido: cos(x) - x")

    # Não aceita coisas que não são expressões numéricas (ex.: "x > 2")
    if not isinstance(expr, sympy.Expr):
        raise ValueError(f"'{texto}' não é uma função de uma variável.")

    variaveis = expr.free_symbols
    if len(variaveis) == 0:
        raise ValueError(f"A função '{texto}' não tem variável (ex.: x ou t).")
    if len(variaveis) > 1:
        nomes = ", ".join(sorted(str(v) for v in variaveis))
        raise ValueError(f"A função deve ter só uma variável, mas encontrei: {nomes}.")

    variavel = list(variaveis)[0]       # a única variável (x, t, ...)
    dexpr = sympy.diff(expr, variavel)  # calcula a derivada
    f = sympy.lambdify(variavel, expr, "math")    # expressão -> função Python
    df = sympy.lambdify(variavel, dexpr, "math")

    return f, df, str(dexpr)


def ler_float(mensagem: str, padrao: float | None = None) -> float:
    """
    Pergunta um número ao usuário até ele digitar algo válido.

    - Aceitar vírgula como separador decimal ("0,5" -> 0.5).
    - Aceitar notação científica ("1e-6").
    - Se padrao não for None e o usuário só apertar Enter, usar o padrão.
    """
    while True:  # repete até o usuário digitar algo válido
        leitura = input(mensagem).strip()  # lê o texto e tira espaços das pontas

        # Enter sem digitar nada: usa o valor padrão, se existir
        if leitura == "" and padrao is not None:
            return padrao

        leitura = leitura.replace(",", ".")  # aceita "0,5" como 0.5

        try:
            valor = float(leitura)  # tenta converter o texto em número
        except ValueError:
            print("  Valor inválido. Digite um número, ex.: 0,5 ou 1e-6")
            continue  # volta para o início do while e pergunta de novo

        # float() aceita "inf" e "nan", que não servem para os métodos
        if not math.isfinite(valor):
            print("  Digite um número finito.")
            continue

        return valor


def ler_int(mensagem: str, padrao: int | None = None) -> int:
    """Igual ao ler_float, mas para inteiros positivos (ex.: max_iter)."""
    while True:  # repete até o usuário digitar algo válido
        leitura = input(mensagem).strip()  # lê o texto e tira espaços das pontas

        # Enter sem digitar nada: usa o valor padrão, se existir
        if leitura == "" and padrao is not None:
            return padrao

        try:
            valor = int(leitura)  # tenta converter o texto em número inteiro
        except ValueError:
            print("  Valor inválido. Digite um número inteiro.")
            continue  # volta para o início do while e pergunta de novo

        # Não faz sentido rodar 0 ou um número negativo de iterações
        if valor <= 0:
            print("  Valor inválido. Digite um número inteiro maior que 0.")
            continue

        return valor


def montar_caso_personalizado() -> dict:
    """
    Pergunta ao usuário a função e os dados iniciais e devolve um dict
    no mesmo formato dos itens de casos.CASOS.
    """
    print("\nDigite a função usando x (ou outra letra) como variável.")
    print("Exemplos: cos(x) - x   |   x^3 - 2*x - 5   |   5*(1 - e^-t) - 3.8")
    print("Use * para multiplicar (2*x, e não 2x). Aceita ^, e, sen, ln.")

    # 1. Função: pergunta até o texto ser válido
    while True:
        texto = input("f(x) = ").strip()
        try:
            f, _, texto_derivada = ler_funcao(texto)
            print(f"  f'(x) calculada: {texto_derivada}")
            break
        except ValueError as erro:
            print(f"  {erro}")

    # 2. Intervalo: pergunta até a < b, e avisa se não há mudança de sinal
    while True:
        a = ler_float("Início do intervalo a: ")
        b = ler_float("Fim do intervalo b: ")
        if a >= b:
            print("  O início a precisa ser menor que o fim b.")
            continue

        try:
            tem_mudanca_de_sinal = f(a) * f(b) < 0
        except (ValueError, ZeroDivisionError, OverflowError):
            print("  A função não pode ser calculada em a ou em b. Escolha outro intervalo.")
            continue

        if tem_mudanca_de_sinal:
            break
        print("  Atenção: f(a) e f(b) têm o mesmo sinal, então Bissecção e Falsa Posição vão falhar.")
        if input("  Usar este intervalo mesmo assim? (s/n): ").strip().lower() == "s":
            break

    # 3. Chutes iniciais: Enter usa as pontas do intervalo (como o enunciado sugere)
    x0_newton = ler_float(f"x0 do Newton (Enter = {a}): ", padrao=a)
    x0_secante = ler_float(f"x0 da Secante (Enter = {a}): ", padrao=a)
    x1_secante = ler_float(f"x1 da Secante (Enter = {b}): ", padrao=b)

    return {
        "nome": f"Função personalizada: {texto}",
        "funcao": texto,
        "a": a, "b": b,
        "x0_newton": x0_newton,
        "x0_secante": x0_secante, "x1_secante": x1_secante,
        "raiz_referencia": None,
    }
