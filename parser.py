# a biblioteca precisa ser instalada: pip install ply
from ply import lex, yacc

# importamos as classes do nosso arquivo arvore.py
from arvore import *

operacoes = ('ATRIBUI', 'MAIS', 'MENOS', 'VEZES', 'DIV')
numeros = ('INT', ) # removemos FLOAT para facilitar a compilação
id = ('ID', )
comparadores = ('IGUAL', 'DIFERENTE', 'MENOR', 'MAIOR', 'MENOR_IGUAL', 'MAIOR_IGUAL')
separadores = ('ABRE_PAREN', 'FECHA_PAREN', 'FIM_STMT', 'ABRE_BLOCO', 'FECHA_BLOCO')

palavras_reservadas = ('PRINT', 'IF', 'ELSE', 'WHILE')

tokens = operacoes + numeros + comparadores + separadores + palavras_reservadas + id

t_ATRIBUI = r'='
t_MAIS = r'\+'
t_MENOS = r'-'
t_VEZES = r'\*'
t_DIV = r'\/'

t_INT = r'\d+'
# t_FLOAT = r'\d+\.\d+'

t_ABRE_PAREN = r'\('
t_FECHA_PAREN = r'\)'
t_FIM_STMT = ';'

t_ABRE_BLOCO = '{'
t_FECHA_BLOCO = '}'

t_IGUAL = '=='
t_DIFERENTE = '!='
t_MENOR = '<'
t_MAIOR = '>'
t_MENOR_IGUAL = '<='
t_MAIOR_IGUAL = '>='

#t_ID = r'[a-zA-Z_]+[a-zA-Z0-9_]*'
#t_PRINT = 'print'

t_ignore = '\t \n\r'

def t_ID(token):
    r'[a-zA-Z_]+[a-zA-Z0-9_]*'
    if token.value.upper() in palavras_reservadas:
        token.type = token.value.upper()
    return token

def t_error(token):
    raise Exception(f'Token não reconhecido: {token.value[0]}')
    
analisador = lex.lex()

# -----------------------------------------------

# Regras de produção da gramática: funções começadas em "p_"

def p_prog(prod):
    'prog : bloco'
    prod[0] = prod[1]

def p_bloco_stmt(prod):
    'bloco : stmt'
    prod[0] = prod[1]

def p_bloco_varios_stmt(prod):
    'bloco : bloco stmt'
    prod[0] = NoBloco(bloco_inicial=prod[1], stmt_final=prod[2])

def p_stmt_atribui(prod):
    'stmt : ID ATRIBUI expr FIM_STMT'
    prod[0] = NoAtribui(id = prod[1], expr=prod[3])

def p_stmt_if(prod):
    'stmt : IF expr stmt'
    prod[0] = NoIfElse(prod[2], prod[3])

def p_stmt_if_else(prod):
    'stmt : IF expr stmt ELSE stmt'
    prod[0] = NoIfElse(prod[2], prod[3], prod[5])

def p_stmt_while(prod):
    'stmt : WHILE expr stmt'
    prod[0] = NoWhile(cond = prod[2], bloco = prod[3])

def p_stmt_expr(prod):
    'stmt : expr FIM_STMT'
    prod[0] = prod[1]

def p_stmt_print(prod):
    'stmt : PRINT ABRE_PAREN expr FECHA_PAREN FIM_STMT'
    prod[0] = NoPrint(expr=prod[3])

def p_stmt_bloco(prod):
    'stmt : ABRE_BLOCO bloco FECHA_BLOCO'
    prod[0] = prod[2]

def p_expr_mais(prod):
    'expr : expr MAIS termo'
    nó = NoOp(tipo = '+')
    nó.filho_esq = prod[1]
    nó.filho_dir = prod[3]
    
    # resultado do parse é o nó criado
    prod[0] = nó 
    
def p_expr_menos(prod):
    'expr : expr MENOS termo'
    nó = NoOp(tipo = '-')
    nó.filho_esq = prod[1]
    nó.filho_dir = prod[3]
    
    # resultado do parse é o nó criado
    prod[0] = nó 

def p_expr_comp(prod):
    'expr : expr compara expr'
    prod[0] = NoOp(tipo=prod[2], filho_esq=prod[1], filho_dir=prod[3])

def p_compara(prod):
    '''compara : IGUAL
        | DIFERENTE
        | MAIOR
        | MAIOR_IGUAL
        | MENOR
        | MENOR_IGUAL'''
    prod[0] = prod[1]

def p_expr_termo(prod):
    'expr : termo'
    
    # resultado é o próprio termo
    prod[0] = prod[1]

def p_termo_vezes(prod):
    'termo : termo VEZES fator'
    prod[0] = NoOp('*', prod[1], prod[3])

def p_termo_div(prod):
    'termo : termo DIV fator'
    prod[0] = NoOp('/', prod[1], prod[3])

def p_termo_fator(prod):
    'termo : fator'
    prod[0] = prod[1]

def p_fator_int(prod):
    'fator : INT'

    prod[0] = NoNum(valor = int(prod[1]))

# def p_fator_float(prod):
#     'fator : FLOAT'

#     prod[0] = NoNum(valor = float(prod[1]))

def p_fator_id(prod):
    'fator : ID'
    prod[0] = NoVar(prod[1])

def p_fator_expr(prod):
    'fator : ABRE_PAREN expr FECHA_PAREN'
    prod[0] = prod[2]

def p_error(p):
    raise SyntaxError('Sintaxe inválida na nossa linguagem!')

'''
Função gera_arvore recebe código-fonte completo na forma de uma
única string.
Em caso de código sem erros léxicos ou sintáticos, retorna a AST
(Árvore de Sintaxe Abstrata) que representa o programa.
'''
def gera_arvore(codigo_fonte : str):
    parser = yacc.yacc()
    arvore = parser.parse(codigo_fonte)
    return arvore