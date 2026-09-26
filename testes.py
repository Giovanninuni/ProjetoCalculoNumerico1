"""
Testes rápidos dos 4 métodos — não dependem de sympy nem do menu.

Como rodar:
    python testes.py

Cada integrante pode rodar isto enquanto implementa sua parte.
Enquanto um método não estiver implementado, os testes dele vão falhar
(é o esperado).
"""

import math

from metodos_intervalo import bisseccao, falsa_posicao
from metodos_abertos import newton_raphson, secante

EPS = 1e-6
MAX_ITER = 100

aprovados = 0
reprovados = 0


def verificar(descricao: str, condicao: bool) -> None:
    global aprovados, reprovados
    if condicao:
        aprovados += 1
        print(f"  OK       {descricao}")
    else:
        reprovados += 1
        print(f"  FALHOU   {descricao}")


def testar_raiz(resultado, raiz_esperada: float) -> None:
    verificar(f"{resultado.metodo}: terminou sem erro ({resultado.erro})", resultado.convergiu)
    if resultado.convergiu:
        verificar(f"{resultado.metodo}: raiz {resultado.raiz:.10f} ~ {raiz_esperada}",
                  abs(resultado.raiz - raiz_esperada) < 1e-5)
        verificar(f"{resultado.metodo}: |f(raiz)| = {resultado.residuo:.2e} < 1e-6",
                  resultado.residuo is not None and resultado.residuo < 1e-6)
        verificar(f"{resultado.metodo}: contou iterações ({resultado.iteracoes})",
                  resultado.iteracoes > 0)


# --- Exemplo de teste do PDF: f(x) = cos(x) - x ---------------------------
print("\nExemplo de teste: cos(x) - x")
f = lambda x: math.cos(x) - x
df = lambda x: -math.sin(x) - 1
RAIZ = 0.7390851332

testar_raiz(bisseccao(f, 0, 1, EPS, MAX_ITER), RAIZ)
testar_raiz(falsa_posicao(f, 0, 1, EPS, MAX_ITER), RAIZ)
testar_raiz(newton_raphson(f, df, 0.5, EPS, MAX_ITER), RAIZ)
testar_raiz(secante(f, 0, 1, EPS, MAX_ITER), RAIZ)

# --- Problema 2: 5(1 - e^-t) - 3.8 ----------------------------------------
print("\nProblema 2: capacitor RC")
g = lambda t: 5 * (1 - math.exp(-t)) - 3.8
dg = lambda t: 5 * math.exp(-t)
RAIZ_RC = -math.log(1 - 3.8 / 5)  # solução exata: t = -ln(0.24) ~ 1.4271

testar_raiz(bisseccao(g, 0, 3, EPS, MAX_ITER), RAIZ_RC)
testar_raiz(falsa_posicao(g, 0, 3, EPS, MAX_ITER), RAIZ_RC)
testar_raiz(newton_raphson(g, dg, 0, EPS, MAX_ITER), RAIZ_RC)
testar_raiz(secante(g, 0, 3, EPS, MAX_ITER), RAIZ_RC)

# --- Falhas que o PDF pede para tratar ------------------------------------
print("\nTratamento de falhas")


def tratou_falha(resultado) -> bool:
    """O método precisa devolver um erro de verdade, não o aviso do esqueleto."""
    return resultado.erro is not None and resultado.erro != "Ainda não implementado"


h = lambda x: x ** 2 - 1  # raízes em -1 e 1

r = bisseccao(h, 2, 3, EPS, MAX_ITER)
verificar(f"Bissecção sem mudança de sinal devolve erro ({r.erro})", tratou_falha(r))

r = falsa_posicao(h, 2, 3, EPS, MAX_ITER)
verificar(f"Falsa Posição sem mudança de sinal devolve erro ({r.erro})", tratou_falha(r))

r = newton_raphson(h, lambda x: 2 * x, 0, EPS, MAX_ITER)
verificar(f"Newton com derivada nula (x0 = 0) devolve erro ({r.erro})", tratou_falha(r))

r = secante(h, -2, 2, EPS, MAX_ITER)  # h(-2) == h(2) -> divisão por zero
verificar(f"Secante com f(x0) == f(x1) devolve erro ({r.erro})", tratou_falha(r))

print(f"\nResumo: {aprovados} OK, {reprovados} falharam.")
