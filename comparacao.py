"""
Comparação: roda os 4 métodos para um caso e mostra os resultados.
Responsável: Giovanni Éber

Recebe um caso (dict no formato de casos.CASOS), executa Bissecção,
Falsa Posição, Newton-Raphson e Secante com os mesmos eps e max_iter
(para a comparação ser justa) e passa os resultados para a saída:
    caso -> entrada.ler_funcao (f e f')
         -> os 4 métodos, cada um protegido por rodar_com_seguranca
         -> relatorio.imprimir_tabela (terminal)
         -> relatorio.mostrar_janela (tabela e gráficos, opcional)
         -> animacao.mostrar_animacoes (seletor de animações, opcional)
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
    # 1. Texto da função -> f e f' (a derivada é calculada pelo sympy)
    f, df, texto_derivada = ler_funcao(caso["funcao"])
    a, b = caso["a"], caso["b"]
    intervalo = (a, b)  # os métodos abertos usam para avisar se saírem dele

    # 2. Mostra os dados usados, para ficarem registrados junto com a tabela
    print(f"\n>>> {caso['nome']}")
    print(f"    f(x) = {caso['funcao']}")
    print(f"    f'(x) = {texto_derivada}   (calculada automaticamente)")
    print(f"    Intervalo [a, b] = [{a}, {b}]")
    print(f"    Newton: x0 = {caso['x0_newton']}   "
          f"Secante: x0 = {caso['x0_secante']}, x1 = {caso['x1_secante']}")
    print(f"    eps = {eps}   max_iter = {max_iter}")

    # 3. Roda os 4 métodos. O lambda adia a chamada para ela acontecer
    #    DENTRO do try de rodar_com_seguranca (senão um erro escaparia)
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

    # 4. Tabela no terminal (sempre) e raiz de referência (só nos casos prontos)
    imprimir_tabela(resultados)

    if caso.get("raiz_referencia") is not None:
        print(f"Raiz de referência: {caso['raiz_referencia']}\n")

    # 5. Janela com tabela e gráficos (Enter = sim). plt.show() espera ela fechar
    resposta = input("Abrir janela com a tabela e os gráficos? (S/n): ").strip().lower()
    if resposta != "n":
        print("Feche a janela para voltar ao menu...")
        subtitulo = (f"f(x) = {caso['funcao']}   ·   [a, b] = [{a}, {b}]   ·   "
                     f"ε = {eps:g}   ·   máx. {max_iter} iterações")
        mostrar_janela(f, a, b, resultados, caso["nome"], subtitulo, eps,
                       raiz_referencia=caso.get("raiz_referencia"))

    # 6. Animação das iterações: seletor com um quadrado por método (Enter = não)
    resposta = input("Ver a animação das iterações de cada método? (s/N): ").strip().lower()
    if resposta == "s":
        mostrar_animacoes(f, resultados, caso, eps, max_iter)
