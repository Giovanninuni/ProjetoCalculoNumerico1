class Resultado:
    def __init__(self, metodo, raiz=None, iteracoes=0, tempo_execucao=0.0, precisao_final=None, historico=None, erro=None):
        self.metodo = metodo
        self.raiz = raiz
        self.iteracoes = iteracoes
        self.tempo_execucao = tempo_execucao
        self.precisao_final = precisao_final
        self.historico = historico if historico is not None else []
        self.erro = erro