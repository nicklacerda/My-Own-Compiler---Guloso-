from parser import gera_arvore
from arvore import *
from contexto import ContextoCodigoLLVM
import shutil
import subprocess
import sys
from pathlib import Path

# arquivo fonte
DIRETORIO = Path(__file__).resolve().parent
NOME_FONTE = 'prog.txt'

# arquivo de saída
NOME_LLVM = 'prog.ll'

# Nome do executável gerado pelo Clang
NOME_EXECUTAVEL = 'prog.exe' if sys.platform == 'win32' else 'prog'

def verifica_arvore(AST : No):
    tabela_simbolos = set()
    try:
        print('Começando análise semântica...')
        AST.verifica(tabela_simbolos)
        print('Análise semântica concluída sem erros.')
        return AST
    except Exception as erro:
        print('Erro na análise semântica:')
        print(erro)

def gera_llvm(AST : No):
    print('Gerando código LLVM...')
    contexto = ContextoCodigoLLVM()
    contexto.adiciona("""
declare i32 @printf(i8*, ...)
@.fmt_int = private unnamed_addr constant [4 x i8] c"%d\\0A\\00", align 1

define i32 @main() {
""")

    AST.gera_llvm(contexto)

    contexto.adiciona("""
    ret i32 0
}
""")

    # usa a lista de instruções para gerar o LLVM completo...
    saida_llvm = '\n'.join(contexto.codigo)

    with open(DIRETORIO / NOME_LLVM, 'w') as arquivo_saida:
        arquivo_saida.write(saida_llvm)
    
    print('Saída gerada com sucesso em ' + NOME_LLVM)

    # Transforma o LLVM em executável usando o Clang instalado no sistema.
    clang = shutil.which('clang') or shutil.which('clang.exe')
    if clang is None:
        caminhos_padrao = (
            Path(r'C:\Program Files\LLVM\bin\clang.exe'),
            Path.home() / 'AppData' / 'Local' / 'Programs' / 'LLVM' / 'bin' / 'clang.exe',
        )
        clang = next((str(caminho) for caminho in caminhos_padrao if caminho.is_file()), None)

    if clang is None:
        raise FileNotFoundError(
            'Clang não encontrado. Instale o LLVM/Clang e adicione o clang ao PATH.'
        )

    subprocess.run(
        [clang, NOME_LLVM, '-o', NOME_EXECUTAVEL],
        check=True,
        cwd=Path(__file__).resolve().parent,
    )
    print('Executável gerado com sucesso em ' + NOME_EXECUTAVEL)

if __name__ == '__main__':
    with open(DIRETORIO / NOME_FONTE) as arquivo:
        entrada = arquivo.read()
    
    try:
        AST = gera_arvore(entrada) # gera AST
        print('Análises léxica e sintática concluídas sem erros.')
    except Exception as erro:
        print(erro)
        exit()
    
    AST_verificada = verifica_arvore(AST)
    if AST_verificada is None:
        exit(1)

    # Com a AST verificada, fazemos a geração de LLVM e do executável
    try:
        gera_llvm(AST_verificada)
    except FileNotFoundError as erro:
        print(erro)
        exit(1)
    except subprocess.CalledProcessError as erro:
        print(f'Erro ao compilar com Clang (código {erro.returncode}).')
        exit(1)