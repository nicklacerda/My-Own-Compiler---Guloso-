class ContextoCodigoLLVM:
    def __init__(self):
        # atributo que guarda quantas variáveis temporárias (registradores) já foram criadas
        self.contador_temp = 0
        
        # controlador de rótulos (labels)
        self.contador_label = 0
        
        # atributo que guarda quais IDs já foram criadas no programa atual
        self.ids = set()
    
        # atributo que guarda o código gerado como lista de linhas
        self.codigo = []
    

    # gera temporarios %1, %2, ...
    def novo_temp(self):
        self.contador_temp += 1
        nome = f'%{self.contador_temp}'
        return nome

    # gera labels: por padrão l_1, l_2 etc mas recebe atributo opcional com o nome específico
    def novo_label(self, prefixo : str = 'l'):
        self.contador_label += 1
        nome = f'{prefixo}_{self.contador_label}'
        return nome
    
    # cria nova variável na pilha via alloca
    # (nessa versão, cria apenas inteiro)
    def adiciona_variavel(self, id : str):
        self.ids.add(id)
        self.adiciona_instrucao(f'%{id} = alloca i32, align 4')
    
    # adiciona uma unica linha, com indentação para dar conta dos labels
    def adiciona_instrucao(self, instrucao : str):
        self.codigo.append(f'    {instrucao}')
    
    # adiciona sem indentação, além disso pode ser uma string de várias
    # linhas se necessário
    def adiciona(self, codigo_texto : str):
        self.codigo.append(codigo_texto)