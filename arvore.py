from contexto import ContextoCodigoLLVM as Contexto

# -----------------------------------------------------------------------------

class No:
    pass

# -----------------------------------------------------------------------------

class NoNum(No):
    # Nó do tipo número. Só guarda o valor numérico.
    def __init__(self, valor):
        self.valor = valor
        
    def verifica(self, st : set):
        pass
    
    # simplesmente retorna seu valor sem gerar instruções LLVM
    def gera_llvm(self, contexto : Contexto):
        return str(self.valor)
    
# -----------------------------------------------------------------------------

class NoBloco(No):
    def __init__(self, bloco_inicial : No = None, stmt_final : No = None):
        self.bloco_inicial = bloco_inicial
        self.stmt_final = stmt_final
    
    def verifica(self, st : set):
        if self.bloco_inicial is not None:
            self.bloco_inicial.verifica(st)
        self.stmt_final.verifica(st)
    
    # gera instruções do bloco inicial e do último stmt recursivamente    
    def gera_llvm(self, contexto : Contexto):
        if self.bloco_inicial is not None:
            self.bloco_inicial.gera_llvm(contexto)
        self.stmt_final.gera_llvm(contexto)

# -----------------------------------------------------------------------------

class NoPrint(No):
    def __init__(self, expr : No):
        self.expr = expr
    
    def verifica(self, st : set):
        self.expr.verifica(st)
        
    def gera_llvm(self, contexto : Contexto):
        val = self.expr.gera_llvm(contexto)
        # Pega o ponteiro da string global @.fmt_int que definimos no cabeçalho
        ptr = contexto.novo_temp()
        contexto.adiciona_instrucao(f'{ptr} = getelementptr inbounds [4 x i8], [4 x i8]* @.fmt_int, i32 0, i32 0')
        
        # Cria um temporário para capturar o retorno do printf
        t_ret = contexto.novo_temp()
        contexto.adiciona_instrucao(f'{t_ret} = call i32 (i8*, ...) @printf(i8* {ptr}, i32 {val})')

# -----------------------------------------------------------------------------

class NoVar(No):
    def __init__(self, id: str):
        self.id = id
    
    def verifica(self, st : set):
        if self.id not in st:
            raise NameError('Variável não definida: ' + self.id)
    
    # dá load e retorna variável temporária com o valor desta variável
    def gera_llvm(self, contexto : Contexto):
        # Variáveis locais moram na pilha via alloca. Precisamos dar load!
        t = contexto.novo_temp()
        contexto.adiciona_instrucao(f"{t} = load i32, i32* %{self.id}, align 4")
        return t

# -----------------------------------------------------------------------------

class NoAtribui(No):
    def __init__(self, id: str, expr: No):
        self.id = id
        self.expr = expr
    
    def verifica(self, st : set):
        self.expr.verifica(st)
        st.add(self.id) # adiciono id aos existentes
    
    def gera_llvm(self, contexto : Contexto):
        # resultado_expr guarda um valor literal ou uma variável temporária que guarda o resultado da expressão
        resultado_expr = self.expr.gera_llvm(contexto)
        
        # se é a primeira atribuição, precisa criar a variável via alloca no LLVM
        if self.id not in contexto.ids:
            contexto.adiciona_variavel(self.id)
        
        contexto.adiciona_instrucao(f'store i32 {resultado_expr}, i32* %{self.id}, align 4')

# -----------------------------------------------------------------------------

class NoIfElse(No):
    def __init__(self, cond : No, bloco_if : No, bloco_else : No = None):
        self.cond = cond
        self.bloco_if = bloco_if
        self.bloco_else = bloco_else
    
    def verifica(self, st : set):
        self.cond.verifica(st)
        self.bloco_if.verifica(st)
        if self.bloco_else is not None:
            self.bloco_else.verifica(st)
    
    def gera_llvm(self, contexto : Contexto):
        # 1. Avalia a condição (retorna um registrador i1)
        val_cond = self.cond.gera_llvm(contexto)
        
        # 2. Cria os labels necessários usando o contexto
        rotulo_then = contexto.novo_label('if_then')
        rotulo_fim = contexto.novo_label('if_fim')
        
        if self.bloco_else is not None:
            rot_else = contexto.novo_label('if_else')
            # Salto condicional com 
            # (br = branch, instrução que escolhe um rótulo ou outro conforme o valor resultante do condicional)
            contexto.adiciona_instrucao(f'br i1 {val_cond}, label %{rotulo_then}, label %{rot_else}')
            
            # Bloco THEN
            contexto.adiciona(f'{rotulo_then}:')
            self.bloco_if.gera_llvm(contexto)
            # faz "branch" (pula) para o fim do if/else
            contexto.adiciona_instrucao(f'br label %{rotulo_fim}') # Fecha o bloco com salto incondicional
            
            # Bloco ELSE
            contexto.adiciona(f'{rot_else}:')
            self.bloco_else.gera_llvm(contexto)
            # faz "branch" (pula) para o fim do if/else
            contexto.adiciona_instrucao(f'br label %{rotulo_fim}') # Fecha o bloco com salto incondicional
        else:
            # Salto condicional sem else (vai direto para o fim se falso)
            contexto.adiciona_instrucao(f'br i1 {val_cond}, label %{rotulo_then}, label %{rotulo_fim}')
            
            # Bloco THEN
            contexto.adiciona(f'{rotulo_then}:')
            self.bloco_if.gera_llvm(contexto)
            contexto.adiciona_instrucao(f'br label %{rotulo_fim}')
            
        # Ponto de encontro (Fim do If)
        contexto.adiciona(f'{rotulo_fim}:')

# -----------------------------------------------------------------------------

class NoWhile(No):
    def __init__(self, cond : No, bloco : No):
        self.cond = cond
        self.bloco = bloco
    
    def verifica(self, st : set):
        self.cond.verifica(st)
        self.bloco.verifica(st)
    
    def gera_llvm(self, contexto : Contexto):
        # O fluxo começa no teste. Ao final do corpo, voltamos à condição.
        rotulo_cond = contexto.novo_label('while_cond')
        rotulo_corpo = contexto.novo_label('while_corpo')
        rotulo_fim = contexto.novo_label('while_fim')

        contexto.adiciona_instrucao(f'br label %{rotulo_cond}')

        contexto.adiciona(f'{rotulo_cond}:')
        val_cond = self.cond.gera_llvm(contexto)
        contexto.adiciona_instrucao(
            f'br i1 {val_cond}, label %{rotulo_corpo}, label %{rotulo_fim}'
        )

        contexto.adiciona(f'{rotulo_corpo}:')
        self.bloco.gera_llvm(contexto)
        contexto.adiciona_instrucao(f'br label %{rotulo_cond}')

        contexto.adiciona(f'{rotulo_fim}:')

# -----------------------------------------------------------------------------

class NoOp(No):
    # Nó do tipo Operação
    # Tem como atributos o tipo (+, -, etc), filho esquerdo e filho direito
    def __init__(self, tipo : str, filho_esq : No = None, filho_dir : No = None):
        self.tipo = tipo
        self.filho_esq = filho_esq
        self.filho_dir = filho_dir
    
    def verifica(self, st : set):
        self.filho_esq.verifica(st)
        self.filho_dir.verifica(st)

        # só verifico divisão por zero no caso mais simples:
        # operando direito é um literal 0
        if self.tipo == '/':
            direito = self.filho_dir
            # se o operando direito for NóNum com valor zero, erro...
            if isinstance(direito, NoNum) and direito.valor == 0:
                raise ValueError('Divisão com operando direito igual a 0')
    
    def gera_llvm(self, contexto : Contexto):
        # resultado esq e dir são os valores ou %temporarios que guardam os operandos esquerdo e direito
        resultado_esq = self.filho_esq.gera_llvm(contexto)
        resultado_dir = self.filho_dir.gera_llvm(contexto)
        t = contexto.novo_temp()

        match self.tipo:
            case '+':
                instrucao = f'{t} = add i32 {resultado_esq}, {resultado_dir}'
            case '-':
                instrucao = f'{t} = sub i32 {resultado_esq}, {resultado_dir}'
            case '*':
                instrucao = f'{t} = mul i32 {resultado_esq}, {resultado_dir}'
            case '/':
                instrucao = f'{t} = sdiv i32 {resultado_esq}, {resultado_dir}'
            case '<':
                instrucao = f'{t} = icmp slt i32 {resultado_esq}, {resultado_dir}'
            case '<=':
                instrucao = f'{t} = icmp sle i32 {resultado_esq}, {resultado_dir}'
            case '>':
                instrucao = f'{t} = icmp sgt i32 {resultado_esq}, {resultado_dir}'
            case '>=':
                instrucao = f'{t} = icmp sge i32 {resultado_esq}, {resultado_dir}'
            case '==':
                instrucao = f'{t} = icmp eq i32 {resultado_esq}, {resultado_dir}'
            case '!=':
                instrucao = f'{t} = icmp ne i32 {resultado_esq}, {resultado_dir}'
        
        contexto.adiciona_instrucao(instrucao)
        return t

# -----------------------------------------------------------------------------