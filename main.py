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


def executar_comparacao(caso: dict, eps: float, max_iter: int) -> None:
    """
    Roda os 4 métodos para um caso e mostra a comparação.

    Passos:
      1. f, df, texto_derivada = ler_funcao(caso["funcao"])
      2. Chamar os 4 métodos com os dados do caso, montando uma lista:
           resultados = [bisseccao(...), falsa_posicao(...),
                         newton_raphson(...), secante(...)]
         (passar intervalo=(caso["a"], caso["b"]) para os abertos,
          para eles poderem avisar se saírem do intervalo)
      3. imprimir_tabela(resultados)
      4. Perguntar se o usuário quer ver os gráficos -> plotar_grafico(...)
    """
    # TODO (Parte 3): implementar
    print("\n[executar_comparacao ainda não implementado]\n")


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

        # TODO (Parte 3): trocar por ler_float/ler_int com os padrões,
        # para o usuário poder mudar eps e max_iter ou só apertar Enter.
        eps = EPS_PADRAO
        max_iter = MAX_ITER_PADRAO

        executar_comparacao(caso, eps, max_iter)


if __name__ == "__main__":
    main()
