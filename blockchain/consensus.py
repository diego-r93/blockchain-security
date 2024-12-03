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
            raise ValueError("Nenhum nó disponível na rede para realizar o consenso.")

        # Filtrar apenas nós com reputação maior que zero
        valid_nodes = [(node_id, data) for node_id, data in nodes if data["reputation"] > 0]
        if not valid_nodes:
            raise ValueError("Nenhum nó com reputação válida disponível para realizar o consenso.")

        # Extrair reputações dos nós válidos
        reputations = np.array([data["reputation"] for _, data in valid_nodes])

        # Normalizar as probabilidades
        probabilities = reputations / reputations.sum()

        # Ajustar o número de proxies ao número de nós válidos
        num_proxies = min(num_proxies, len(valid_nodes))

        try:
            selected_nodes = np.random.choice(
                [node[0] for node in valid_nodes], size=num_proxies, replace=False, p=probabilities
            )
            return selected_nodes
        except ValueError as e:
            raise ValueError(f"Erro ao selecionar proxy nodes: {e}. Nodes: {valid_nodes}, Probabilidades: {probabilities}")

    def validate_transaction(self, transaction):
        """
        Valida os dados de uma transação.
        """
        temperature = transaction.get("temperature")
        humidity = transaction.get("humidity")

        if 10 <= temperature <= 30 and 30 <= humidity <= 80:
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

    def reward_node(self, node_id):
        """
        Aumenta a reputação de um nó.
        """
        if node_id in self.network:
            current_reputation = self.network.nodes[node_id]["reputation"]
            self.network.nodes[node_id]["reputation"] = min(1.0, current_reputation + 0.1)
            print(f"Nó {node_id} recompensado. Nova reputação: {self.network.nodes[node_id]['reputation']}")

    def consensus_round(self, proxy_nodes, transaction):
        """
        Realiza uma rodada de consenso entre os proxy nodes.
        """
        approvals = 0
        total_votes = len(proxy_nodes)

        for node in proxy_nodes:
            if self.validate_transaction(transaction):
                if random.random() < 0.9:
                    approvals += 1
                    self.reward_node(node)  # Recompensa o nó por aprovar uma transação válida
            else:
                self.penalize_node(node)  # Penaliza o nó por rejeitar ou validar uma transação inválida

        print(f"Consenso: {approvals}/{total_votes} aprovações.")
        return approvals > total_votes / 2, approvals
