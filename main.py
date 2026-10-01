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

    # 3. Chutes iniciais: Enter usa as pontas do intervalo (como o PDF sugere)
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
