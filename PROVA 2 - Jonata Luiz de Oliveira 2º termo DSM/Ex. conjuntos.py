from node import Node
from lista import Lista
from pilha import Pilha
from fila import Fila

class Node:
    def __init__(self, dado):
        self.item = dado
        self.prox = None

    def __str__(self):
        return str(self.item)

class Lista:
    def __init__(self):
        self.cabeca = None

    def esta_vazia(self):
        return self.cabeca is None

    def inserir_inicio(self, dado):
        novo = Node(dado)
        novo.prox = self.cabeca
        self.cabeca = novo

    def inserir_fim(self, dado):
        novo = Node(dado)
        if self.esta_vazia():
            self.cabeca = novo
            return
        atual = self.cabeca
        while atual.prox:
            atual = atual.prox
        atual.prox = novo

    def imprimir_lista(self):
        atual = self.cabeca
        elementos = []
        while atual:
            elementos.append(str(atual.item))
            atual = atual.prox
        print(" -> ".join(elementos) if elementos else "Lista Vazia")

    # --- 1. Exercícios de percurso em lista ---

    def min(self):
        """Retorna o menor elemento da lista."""
        if self.esta_vazia():
            return None
        menor = self.cabeca.item
        atual = self.cabeca.prox
        while atual:
            if atual.item < menor:
                menor = atual.item
            atual = atual.prox
        return menor

    def max(self):
        """Retorna o maior elemento da lista."""
        if self.esta_vazia():
            return None
        maior = self.cabeca.item
        atual = self.cabeca.prox
        while atual:
            if atual.item > maior:
                maior = atual.item
            atual = atual.prox
        return maior

    def sum(self):
        """Retorna a soma dos elementos numéricos da lista."""
        soma = 0
        atual = self.cabeca
        while atual:
            soma += atual.item
            atual = atual.prox
        return soma

    def len(self):
        """Retorna a quantidade de elementos da lista."""
        contador = 0
        atual = self.cabeca
        while atual:
            contador += 1
            atual = atual.prox
        return contador

    def avg(self):
        """Retorna a média dos elementos numéricos da lista."""
        total_elementos = self.len()
        if total_elementos == 0:
            return 0
        return self.sum() / total_elementos

    # --- 2. Exercícios gerais de lista ---

    def append(self, outra_lista):
        """Concatena uma segunda lista no final da lista principal."""
        if outra_lista.esta_vazia():
            return

        if self.esta_vazia():
            self.cabeca = outra_lista.cabeca
            return

        atual = self.cabeca
        while atual.prox:
            atual = atual.prox
        atual.prox = outra_lista.cabeca

    def reverse(self):
        """Inverte toda a ordem de indexação/encadeamento da lista."""
        anterior = None
        atual = self.cabeca
        while atual:
            proximo = atual.prox
            atual.prox = anterior
            anterior = atual
            atual = proximo
        self.cabeca = anterior
   
    if __name__ == "__main__":
        pass  # O código de teste será colocado em Ex1.py
    # --- Teste de Lista ---
    print("=== TESTE DA LISTA ===")
    l1 = Lista()
    for x in [10, 5, 20, 15, 5]:
        l1.inserir_fim(x)

    l1.imprimir_lista()
    print("Menor:", l1.min())
    print("Maior:", l1.max())
    print("Soma:", l1.sum())
    print("Tamanho:", l1.len())
    print("Média:", l1.avg())

    l2 = Lista()
    l2.inserir_fim(30)
    l2.inserir_fim(40)

    l1.append(l2)
    print("Após append:")
    l1.imprimir_lista()

    l1.reverse()
    print("Após reverse:")
    l1.imprimir_lista()

    # --- Teste de Pilha ---
    print("\n=== TESTE DA PILHA ===")
    p = Pilha()
    for x in [1, 2, 3, 2, 4, 1]:
        p.push(x)

    p.imprimir_pilha()
    print("Busca 3:", p.buscar(3))
    p.editar(3, 99)
    print("Após editar 3 para 99:")
    p.imprimir_pilha()

    p.remover(2)
    print("Após remover o primeiro 2:")
    p.imprimir_pilha()

    p.remover_repetidos()
    print("Após remover repetidos:")
    p.imprimir_pilha()

    # --- Teste de Fila ---
    print("\n=== TESTE DA FILA ===")
    f = Fila()
    for x in [10, 20, 10, 30, 20, 40]:
        f.enqueue(x)

    f.imprimir_fila()
    print("Busca 30:", f.buscar(30))
    f.editar(20, 25)
    print("Após editar 20 para 25:")
    f.imprimir_fila()

    f.remover(30)
    print("Após remover 30:")
    f.imprimir_fila()

    f.remover_repetidos()
    print("Após remover repetidos:")
    f.imprimir_fila()