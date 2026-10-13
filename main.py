"""
Simulador de Resolução de Equações Algébricas e Transcendentes.
Cálculo Numérico — UNIVASF 2026.2 — Projeto Unidade 1 (Zeros)

Equipe: Giovanni Éber, Caio Benevides, Tãua Oliveira

Como executar:
    pip install -r requirements.txt
    python main.py

PARTE 3 — Menu principal: escolhe o caso, lê eps e max_iter e chama a
comparação. O trabalho de verdade está nos outros arquivos:
    entrada.py     -> leitura dos dados (função, números, caso personalizado)
    comparacao.py  -> roda os 4 métodos e mostra os resultados
"""

from casos import CASOS, EPS_PADRAO, MAX_ITER_PADRAO
from comparacao import executar_comparacao
from entrada import ler_float, ler_int, montar_caso_personalizado


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
