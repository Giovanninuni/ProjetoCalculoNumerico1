"""
Resultado: o formato que os 4 métodos devolvem.

Fluxo: cada método (metodos_intervalo.py, metodos_abertos.py) preenche um
Resultado; relatorio.py e animacao.py só leem estes campos para montar a
tabela, os gráficos e as animações, sem saber como cada método calcula.

erro x aviso:
    erro  -> o método falhou e a raiz não vale (ex.: sem mudança de sinal);
    aviso -> o método convergiu, mas algo merece registro
             (ex.: um método aberto saiu do intervalo e voltou).
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
