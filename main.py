"""
Simulador de Resolução de Equações Algébricas e Transcendentes.
Cálculo Numérico — UNIVASF 2026.2 — Projeto Unidade 1 (Zeros)

Equipe: Giovanni Éber, Caio Benevides, Tãua Oliveira

Como executar:
    pip install -r requirements.txt
    python main.py

PARTE 3 — Menu principal: junta entrada, métodos e relatório.
"""

from casos import CASOS, EPS_PADRAO, MAX_ITER_PADRAO
from entrada import ler_funcao, ler_float, ler_int
from metodos_intervalo import bisseccao, falsa_posicao
from metodos_abertos import newton_raphson, secante
from relatorio import imprimir_tabela, plotar_grafico
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

    # TODO (Parte 3): abrir a janela com tabela e gráficos (relatorio.mostrar_janela)


def montar_caso_personalizado() -> dict:
    """
    Pergunta ao usuário a função e os dados iniciais e devolve um dict
    no mesmo formato dos itens de casos.CASOS.
    """
    # TODO (Parte 3): implementar usando ler_float
    raise NotImplementedError


def main() -> None:
    while True:
        print("=" * 60)
        print(" SIMULADOR DE ZEROS DE FUNÇÕES — Comparativo de Métodos")
        print("=" * 60)
        for i, caso in enumerate(CASOS, start=1):
            print(f" {i}. {caso['nome']}")
        opcao_personalizada = len(CASOS) + 1
        print(f" {opcao_personalizada}. Digitar outra função")
        print(" 0. Sair")

        escolha = input("\nEscolha uma opção: ").strip()

        if escolha == "0":
            print("Até mais!")
            break

        if not escolha.isdigit() or not 1 <= int(escolha) <= opcao_personalizada:
            print("Opção inválida, tente novamente.\n")
            continue

        numero = int(escolha)
        caso = CASOS[numero - 1] if numero <= len(CASOS) else montar_caso_personalizado()

        # O usuário pode mudar eps e max_iter ou só apertar Enter para usar o padrão
        eps = ler_float(f"Precisão eps (Enter = {EPS_PADRAO}): ", padrao=EPS_PADRAO)
        max_iter = ler_int(f"Máximo de iterações (Enter = {MAX_ITER_PADRAO}): ",
                           padrao=MAX_ITER_PADRAO)

        executar_comparacao(caso, eps, max_iter)


if __name__ == "__main__":
    main()
