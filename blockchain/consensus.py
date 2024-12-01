import networkx as nx
import random
import numpy as np

class ConsensusManager:
    def __init__(self):
        self.network = nx.Graph()

    def add_node(self, node_id, reputation=None):
        """
        Adiciona um node à rede com uma reputação inicial.
        """
        reputation = reputation or random.uniform(0.5, 1.0)
        self.network.add_node(node_id, reputation=reputation)

    def select_proxy_nodes(self, num_proxies=3):
        """
        Seleciona proxy nodes com base na reputação.
        """
        nodes = list(self.network.nodes(data=True))
        
        if not nodes:
            raise ValueError("Nenhum node disponível na rede para realizar o consenso.")

        reputations = np.array([data["reputation"] for _, data in nodes])

        # Verifica se todas as reputações são 0 ou a soma é 0
        if reputations.sum() == 0:
            probabilities = np.ones(len(reputations)) / len(reputations)  # Probabilidades iguais
        else:
            probabilities = reputations / reputations.sum()  # Normaliza as reputações para somar 1

        # Garante que o número de proxy nodes não exceda o número de nodes disponíveis
        num_proxies = min(num_proxies, len(nodes))

        try:
            selected_nodes = np.random.choice(
                [node[0] for node in nodes], size=num_proxies, replace=False, p=probabilities
            )
            return selected_nodes
        except ValueError as e:
            raise ValueError(f"Erro ao selecionar proxy nodes: {e}. Nodes: {nodes}, Probabilidades: {probabilities}")

    def validate_transaction(self, transaction):
        """
        Valida os dados de uma transação.
        """
        temperature = transaction.get("temperature")
        humidity = transaction.get("humidity")

        # Dados válidos estão no intervalo esperado
        if 20 <= temperature <= 30 and 30 <= humidity <= 50:
            return True
        return False

    def penalize_node(self, node_id):
        """
        Reduz a reputação de um nó.
        """
        if node_id in self.network:
            current_reputation = self.network.nodes[node_id]["reputation"]
            self.network.nodes[node_id]["reputation"] = max(0, current_reputation - 0.1)
            print(f"Nó {node_id} penalizado. Nova reputação: {self.network.nodes[node_id]['reputation']}")

    def consensus_round(self, proxy_nodes, transaction):
        """
        Realiza uma rodada de consenso entre os proxy nodes.
        """
        approvals = 0
        total_votes = len(proxy_nodes)

        for node in proxy_nodes:
            # Simula validação da transação pelo proxy node
            if self.validate_transaction(transaction):
                # Proxy node aprova a transação com 90% de chance
                if random.random() < 0.9:
                    approvals += 1
            else:
                # Penaliza o proxy node se ele validar uma transação inválida
                self.penalize_node(node)

        # Retorna o resultado do consenso
        if approvals > total_votes / 2:
            return True, approvals  # Consenso alcançado
        else:
            return False, approvals  # Consenso falhou