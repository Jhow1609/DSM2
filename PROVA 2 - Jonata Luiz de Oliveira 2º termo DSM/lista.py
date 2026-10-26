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
           