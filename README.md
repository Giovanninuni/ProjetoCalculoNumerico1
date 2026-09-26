# ProjetoCalculoNumerico1

Simulador de Resolução de Equações Algébricas e Transcendentes — compara
**Bissecção, Falsa Posição, Newton-Raphson e Secante** (raiz, iterações,
tempo de execução e |f(raiz)|).

Cálculo Numérico — UNIVASF 2026.2 — Projeto Unidade 1 (Zeros).
Enunciado completo: [ProjetoCalculoNumeroInstrucoes.pdf](ProjetoCalculoNumeroInstrucoes.pdf)

## Como executar

```bash
pip install -r requirements.txt
python main.py      # programa com menu
python testes.py    # testes dos 4 métodos
```

## Estrutura

| Arquivo | Conteúdo | Responsável |
|---|---|---|
| `resultado.py` | Classe `Resultado` — formato que **todos** os métodos devolvem | Equipe |
| `metodos_intervalo.py` | Bissecção e Falsa Posição | Parte 1 |
| `metodos_abertos.py` | Newton-Raphson e Secante | Parte 2 |
| `entrada.py` | Leitura da função (sympy, derivada automática) e dos números | Parte 3 |
| `relatorio.py` | Tabela comparativa e gráficos (matplotlib) | Parte 3 |
| `casos.py` | Casos prontos do enunciado (exemplo, Problema 1 e 2) | Parte 3 |
| `main.py` | Menu: escolher caso, novo cálculo ou sair | Parte 3 |
| `testes.py` | Testes dos métodos, sem depender do menu | Equipe |

## Divisão da equipe

| | Parte 1 — Métodos de intervalo | Parte 2 — Métodos abertos | Parte 3 — Interface e saída |
|---|---|---|---|
| **Quem** | _a definir_ | _a definir_ | Giovanni Éber |
| **Código** | Bissecção, Falsa Posição | Newton-Raphson, Secante | Menu, entrada, tabela, gráficos |
| **Falhas tratadas** | Sem mudança de sinal, divisão por zero | Derivada nula, divisão por zero, saída do intervalo | Entrada inválida |
| **Relatório** | Por que sempre convergem, mas são lentos | Por que são rápidos, mas podem falhar | Como executar, gráficos, relevância do circuito RC |

Análise crítica e conclusão do relatório: equipe toda.

## Combinados

- Critério de parada igual para os 4 métodos: `|f(x)| < eps` **ou** `|x_novo - x_anterior| < eps`.
- Mesmos `eps = 1e-6` e `max_iter = 100` em todos os métodos (o PDF pede comparação justa).
- Cada um mexe principalmente no seu arquivo, para evitar conflitos no Git.
- Todo método devolve um `Resultado` — nunca usa `print` nem `input` (quem mostra é o `relatorio.py`).

## Prazos

- Apresentação: 13 ou 15/10/2026 (sorteio) — **todos precisam estar presentes**
- Relatório final (PDF): 16/10/2026
