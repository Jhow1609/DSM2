class Node:
    def __init__(self, dado):
        self.item = dado
        self.prox = None

    def __str__(self):
        return str(self.item)

class Pilha:
    def __init__(self):
        self.topo = None

    def esta_vazia(self):
        return self.topo is None

    def push(self, dado):
        novo = Node(dado)
        novo.prox = self.topo
        self.topo = novo

    def pop(self):
        if self.esta_vazia():
            return None
        removido = self.topo.item
        self.topo = self.topo.prox
        return removido

    def imprimir_pilha(self):
        atual = self.topo
        elementos = []
        while atual:
            elementos.append(str(atual.item))
            atual = atual.prox
        print("Topo -> " + " -> ".join(elementos) if elementos else "Pilha Vazia")

    # --- 3. Exercícios de pilha ---

    def buscar(self, info):
        """Busca um elemento na pilha e retorna True se encontrado."""
        atual = self.topo
        while atual:
            if atual.item == info:
                return True
            atual = atual.prox
        return False

    def editar(self, info_antiga, info_nova):
        """Edita a primeira ocorrência de um elemento na pilha."""
        atual = self.topo
        while atual:
            if atual.item == info_antiga:
                atual.item = info_nova
                return True
            atual = atual.prox
        return False

    def remover(self, info):
        """Busca e remove a primeira ocorrência de um elemento na pilha."""
        if self.esta_vazia():
            return False

        if self.topo.item == info:
            self.topo = self.topo.prox
            return True

        atual = self.topo
        while atual.prox:
            if atual.prox.item == info:
                atual.prox = atual.prox.prox
                return True
            atual = atual.prox
        return False

    def remover_repetidos(self):
        """Remove todos os valores repetidos da pilha, mantendo apenas a primeira aparição."""
        vistos = set()
        atual = self.topo
        anterior = None

        while atual:
            if atual.item in vistos:
                anterior.prox = atual.prox
            else:
                vistos.add(atual.item)
                anterior = atual
            atual = atual.prox