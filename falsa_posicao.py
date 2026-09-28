import time
from resultado import Resultado

def falsa_posicao(f, a, b, eps=1e-6, max_iter=100):
    inicio_tempo = time.perf_counter()
    historico = []
    
    # Checagem de falha: sem mudança de sinal
    if f(a) * f(b) >= 0:
        return Resultado(metodo="Falsa Posição", erro="Falha: Sem mudança de sinal no intervalo inicial.")
    
    x_anterior = None
    
    for iteracao in range(1, max_iter + 1):
        fa = f(a)
        fb = f(b)
        
        # Checagem de falha: Divisão por zero
        if fb - fa == 0:
            return Resultado(metodo="Falsa Posição", erro="Falha: Divisão por zero (f(b) = f(a)).")
            
        x = (a * fb - b * fa) / (fb - fa)
        historico.append(x)
        
        # Critério de parada
        if abs(f(x)) < eps or (x_anterior is not None and abs(x - x_anterior) < eps):
            tempo_fim = time.perf_counter()
            return Resultado(
                metodo="Falsa Posição", 
                raiz=x, 
                iteracoes=iteracao,
                tempo_execucao=tempo_fim - inicio_tempo, 
                precisao_final=abs(f(x)),
                historico=historico
            )
        
        # Atualização do intervalo mantendo a raiz
        if fa * f(x) < 0:
            b = x
        else:
            a = x
            
        x_anterior = x

    return Resultado(metodo="Falsa Posição", erro="Falha: Não convergiu após o número máximo de iterações.")

# ==========================================
# ÁREA DE TESTE LOCAL
# ==========================================
if __name__ == "__main__":
    import math

    # Função de teste do PDF: f(x) = cos(x) - x
    def f_teste(x):
        return math.cos(x) - x

    print("=== Teste Local: Método da Falsa Posição ===")
    
    # O exemplo do PDF pede intervalo [0, 1]
    resultado = falsa_posicao(f_teste, 0, 1)

    if not resultado.erro:
        print(f"Raiz encontrada: {resultado.raiz:.10f} (Referência: ~0.7390851332)")
        print(f"Iterações: {resultado.iteracoes}")
        print(f"Tempo: {resultado.tempo_execucao:.6f} segundos")
        print(f"Precisão final |f(x)|: {resultado.precisao_final}")
    else:
        print(resultado.erro)