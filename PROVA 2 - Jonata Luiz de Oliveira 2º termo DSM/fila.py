class Node:
    def __init__(self, dado):
        self.item = dado
        self.prox = None

    def __str__(self):
        return str(self.item)

class Fila:
    def __init__(self):
        self.inicio = None
        self.fim = None

    def esta_vazia(self):
        return self.inicio is None

    def enqueue(self, dado):
        novo = Node(dado)
        if self.esta_vazia():
            self.inicio = novo
            self.fim = novo
        else:
            self.fim.prox = novo
            self.fim = novo

    def dequeue(self):
        if self.esta_vazia():
            return None
        removido = self.inicio.item
        self.inicio = self.inicio.prox
        if self.inicio is None:
            self.fim = None
        return removido

    # --- 4. Exercícios de Fila ---

    def imprimir_fila(self):
        """Imprime os elementos da fila do início ao fim."""
        atual = self.inicio
        elementos = []
        while atual:
            elementos.append(str(atual.item))
            atual = atual.prox
        print("Início -> " + " -> ".join(elementos) + " <- Fim" if elementos else "Fila Vazia")

    def buscar(self, info):
        """Busca um elemento na fila e retorna True se encontrado."""
        atual = self.inicio
        while atual:
            if atual.item == info:
                return True
            atual = atual.prox
        return False

    def editar(self, info_antiga, info_nova):
        """Edita a primeira ocorrência de um elemento na fila."""
        atual = self.inicio
        while atual:
            if atual.item == info_antiga:
                atual.item = info_nova
                return True
            atual = atual.prox
        return False

    def remover(self, info):
        """Busca e remove a primeira ocorrência de um elemento da fila."""
        if self.esta_vazia():
            return False

        if self.inicio.item == info:
            self.inicio = self.inicio.prox
            if self.inicio is None:
                self.fim = None
            return True

        atual = self.inicio
        while atual.prox:
            if atual.prox.item == info:
                if atual.prox == self.fim:
                    self.fim = atual
                atual.prox = atual.prox.prox
                return True
            atual = atual.prox
        return False

    def remover_repetidos(self):
        """Remove todas as repetições de elementos na fila."""
        vistos = set()
        atual = self.inicio
        anterior = None

        while atual:
            if atual.item in vistos:
                anterior.prox = atual.prox
                if atual == self.fim:
                    self.fim = anterior
            else:
                vistos.add(atual.item)
                anterior = atual
            atual = atual.prox