"""
PARTE 3 — Casos prontos do enunciado, para o menu oferecer sem o usuário
precisar digitar tudo.

As funções ficam como TEXTO (ex.: "cos(x) - x"); quem transforma o texto
em função de verdade é o entrada.py (com sympy).

REVISAR em equipe: os intervalos dos Problemas 1 e 2 foram escolhidos
por nós (o enunciado pede para a equipe definir). Conferir que há
mudança de sinal: f(a) e f(b) com sinais opostos.
"""

EPS_PADRAO = 1e-6
MAX_ITER_PADRAO = 100

CASOS = [
    {
        "nome": "Exemplo de teste: f(x) = cos(x) - x",
        "funcao": "cos(x) - x",
        "a": 0.0, "b": 1.0,           # Bissecção e Falsa Posição
        "x0_newton": 0.5,             # Newton-Raphson
        "x0_secante": 0.0, "x1_secante": 1.0,  # Secante
        "raiz_referencia": 0.7390851332,
    },
    {
        "nome": "Problema 1: resfriamento, 20 + 90e^(-0.15t) - 50",
        "funcao": "20 + 90*exp(-0.15*t) - 50",
        # f(0) = 60 > 0 e f(20) ~ -25.5 < 0  ->  há raiz em [0, 20]
        "a": 0.0, "b": 20.0,
        "x0_newton": 0.0,
        "x0_secante": 0.0, "x1_secante": 20.0,
        "raiz_referencia": None,      # TODO: preencher depois de rodar (~7.32)   
    },
    {
        
        "nome": "Problema 2: capacitor RC, 5(1 - e^-t) - 3.8",
        "funcao": "5*(1 - exp(-t)) - 3.8",
        # f(0) = -3.8 < 0 e f(3) ~ 0.95 > 0  ->  há raiz em [0, 3]
        "a": 0.0, "b": 3.0,
        "x0_newton": 0.0,             # enunciado: uma das extremidades
        "x0_secante": 0.0, "x1_secante": 3.0,
        "raiz_referencia": None,      # TODO: preencher depois de rodar (~1.427)
    },
]
