# Projeto 2

Nesta etapa do projeto, quero que vocês vejam como é possível adaptar nosso interpretador para gerar um compilador de fato.

Esse compilador funciona assim:
1. Usa a tokenização e análise sintática igual às do interpretador, produzindo uma AST (árvore de sintaxe abstrata) correspondente ao código-fonte;

2. Faz uma verificação semântica básica na AST (apenas verifica uso de variáveis não definidas e divisão por zero);

3. Implementa em cada nó da árvore um método que gera código LLVM;

4. Usa o compilador CLANG para transformar o LLVM (arquivo prog.ll) em programa executável.

## Informações básicas

* Data de entrega e arguição: **25/11/2026**
* Projeto individual ou em dupla
* Nota do projeto: 0,5\*C + 0,5\*A, onde
    - C = nota obtida no código
    - A = nota obtida na arguição. É individual e fica igual a 0 em caso de ausência no dia da arguição.

## O código fornecido

São fornecidos os seguintes arquivos já prontos:

* `compilador.py` : arquivo principal. Lê o código-fonte e usa o analisador sintático (parser) que já tínhamos antes para produzir a árvore. Depois chama a verificação semântica e gera o LLVM, produzindo a saída `prog.ll`.

* `parser.py` : arquivo em que se deifnem os tokens e as regras gramaticais.

* `arvore.py` : define as classes que compõem a AST (árvore de sintaxe abstrata). Quase igual à vista em aula para o interpretador, com as seguintes mudanças:
    - O bloco de código agora é recursivo à esquerda. (Em vez de `primeiro_stmt` e `bloco_restante`, temos um `bloco_inicial` e `stmt_final`);

    - Não temos mais o método `avalia()`, que realizava a interpretação dos nós;

    - Temos um método `verifica()`, que faz análise semântica. É usada uma tabela de símbolos (`st`) mais simples: apenas um dicionário que guarda quais IDs já foram criados;

    - Temos um método `gera_llvm()`, que produz instruções LLVM correspondentes a cada nó de maneira recursiva.
    O método `gera_llvm()` recebe um *contexto*, que é um novo conceito, explicado a seguir.

* `contexto.py` : define uma classe `ContextoCodigoLLVM`, responsável por manter certas informações acerca do código LLVM gerado (por exemplo: numeração das variáveis temporárias e dos rótulos), além de guardar a sequência de instruções geradas.

## Sua tarefa

Estão faltando duas coisas no código fornecido:
1. Implementar a geração de LLVM do nó `While`. Pense como fica a estrutura de labels para implementar o `While` e então se baseie na implementação fornecida do `IfElse` para fazer algo similar;

2. Automatizar a etapa de transformar o `prog.ll` em executável. Você irá colocar essa lógica no `compilador.py`. Para isso, é necessário instalar o LLVM/Clang no seu computador para poder chamar o compilador `clang`.

## Dúvidas?

Para mais esclarecimentos, você pode procurar o professor na aula da próxima segunda-feira (23/11).
