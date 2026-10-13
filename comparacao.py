"""
PARTE 3 — Comparação: roda os 4 métodos para um caso e mostra os resultados.

Recebe um caso (dict no formato de casos.CASOS), executa Bissecção,
Falsa Posição, Newton-Raphson e Secante com os mesmos eps e max_iter,
e mostra a tabela no terminal, a janela com gráficos e as animações.
"""

from animacao import mostrar_animacoes
from entrada import ler_funcao
from metodos_abertos import newton_raphson, secante
from metodos_intervalo import bisseccao, falsa_posicao
from relatorio import imprimir_tabela, mostrar_janela
from resultado import Resultado


def rodar_com_seguranca(nome_metodo: str, chamada) -> Resultado:
    """
    Executa um método e, se ele quebrar com um erro matemático
    (ex.: ln de número negativo, overflow), devolve um Resultado com
    a falha em vez de derrubar o programa inteiro.
    """
    try:
        return chamada()
    except (ValueError, ZeroDivisionError, OverflowError) as erro:
        return Resultado(nome_metodo, erro=f"Falha: erro matemático ({erro})")


def executar_comparacao(caso: dict, eps: float, max_iter: int) -> None:
    """Roda os 4 métodos para um caso e mostra a comparação."""
    f, df, texto_derivada = ler_funcao(caso["funcao"])
    a, b = caso["a"], caso["b"]
    intervalo = (a, b)  # os métodos abertos usam para avisar se saírem dele

    # Mostra os dados usados, para ficar registrado junto com a tabela
    print(f"\n>>> {caso['nome']}")
    print(f"    f(x) = {caso['funcao']}")
    print(f"    f'(x) = {texto_derivada}   (calculada automaticamente)")
    print(f"    Intervalo [a, b] = [{a}, {b}]")
    print(f"    Newton: x0 = {caso['x0_newton']}   "
          f"Secante: x0 = {caso['x0_secante']}, x1 = {caso['x1_secante']}")
    print(f"    eps = {eps}   max_iter = {max_iter}")

    resultados = [
        rodar_com_seguranca("Bissecção",
                            lambda: bisseccao(f, a, b, eps, max_iter)),
        rodar_com_seguranca("Falsa Posição",
                            lambda: falsa_posicao(f, a, b, eps, max_iter)),
        rodar_com_seguranca("Newton-Raphson",
                            lambda: newton_raphson(f, df, caso["x0_newton"],
                                                   eps, max_iter, intervalo)),
        rodar_com_seguranca("Secante",
                            lambda: secante(f, caso["x0_secante"], caso["x1_secante"],
                                            eps, max_iter, intervalo)),
    ]

    imprimir_tabela(resultados)

    if caso.get("raiz_referencia") is not None:
        print(f"Raiz de referência: {caso['raiz_referencia']}\n")

    # Janela com tabela e gráficos (Enter = sim)
    resposta = input("Abrir janela com a tabela e os gráficos? (S/n): ").strip().lower()
    if resposta != "n":
        print("Feche a janela para voltar ao menu...")
        subtitulo = (f"f(x) = {caso['funcao']}   ·   [a, b] = [{a}, {b}]   ·   "
                     f"ε = {eps:g}   ·   máx. {max_iter} iterações")
        mostrar_janela(f, a, b, resultados, caso["nome"], subtitulo, eps)

    # Animação das iterações: seletor com um quadrado por método (Enter = não)
    resposta = input("Ver a animação das iterações de cada método? (s/N): ").strip().lower()
    if resposta == "s":
        mostrar_animacoes(f, resultados, caso, eps, max_iter)
