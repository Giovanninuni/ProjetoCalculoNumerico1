"""
Formato de resultado compartilhado por TODOS os métodos.

É o "contrato" da equipe: toda função de método devolve um Resultado,
então a Parte 3 (tabela e gráficos) não precisa saber como cada método
funciona por dentro — só lê estes campos.
"""

from dataclasses import dataclass, field


@dataclass
class Resultado:
    metodo: str                  # Nome do método, ex.: "Bissecção"
    raiz: float | None = None    # Raiz encontrada (None se o método falhou)
    iteracoes: int = 0           # Quantas iterações foram feitas
    tempo_ms: float = 0.0        # Tempo de execução em milissegundos
    residuo: float | None = None  # Precisão final |f(raiz)|
    erro: str | None = None      # Mensagem de falha (None se deu certo)
    aviso: str | None = None     # Algo notável que não é falha (ex.: saiu do intervalo e voltou)
    historico: list[float] = field(default_factory=list)  # Aproximação de cada iteração (usado nos gráficos)

    @property
    def convergiu(self) -> bool:
        """True se o método terminou sem erro e encontrou uma raiz."""
        return self.erro is None and self.raiz is not None
