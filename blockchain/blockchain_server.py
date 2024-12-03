from flask import Flask, request, jsonify
from blockchain import Blockchain, generate_public_key
from consensus import ConsensusManager

# Inicialização do consenso e blockchain
consensus_manager = ConsensusManager()

PRIVATE_KEY = "f6c93994817fddff529c65f477b6631e8a5e64454e0eb903f4f5bb191e2c84f4"
PUBLIC_KEY = generate_public_key(PRIVATE_KEY)

blockchain = Blockchain(PRIVATE_KEY, PUBLIC_KEY)

app = Flask(__name__)

@app.route('/add_device', methods=['POST'])
def add_device():
    data = request.json
    print(f"Recebido para registro: {data}")  # Log para verificar o payload
    node_id = data.get("device_id")
    if node_id:
        consensus_manager.add_node(node_id)
        print(f"Dispositivo {node_id} registrado com sucesso.")  # Log para sucesso
        return jsonify({"message": "Device added with max reputation.", "device_id": node_id}), 201
    print("Erro: device_id ausente.")  # Log para erro
    return jsonify({"error": "Missing device_id"}), 400

@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.json
    device_id = data.get("device_id")

    if not device_id or device_id not in consensus_manager.network.nodes:
        return jsonify({"error": "Device not registered"}), 400

    proxy_nodes = consensus_manager.select_proxy_nodes()
    consensus, approvals = consensus_manager.consensus_round(proxy_nodes, data)

    if consensus:
        reputation = consensus_manager.network.nodes[device_id]["reputation"]
        data["reputation"] = reputation
        blockchain.add_block(data)
        return jsonify({"message": "Block added with consensus.", "reputation": reputation, "approvals": approvals}), 201
    else:
        consensus_manager.penalize_node(device_id)
        return jsonify({"error": "Consensus failed.", "approvals": approvals}), 400

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [block.to_dict() for block in blockchain.chain]
    return jsonify(chain_data), 200

@app.route('/validate_chain', methods=['GET'])
def validate_chain():
    if blockchain.is_chain_valid():
        return jsonify({"message": "Blockchain is valid"}), 200
    else:
        return jsonify({"message": "Blockchain is invalid"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)