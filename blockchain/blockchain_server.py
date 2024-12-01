from flask import Flask, request, jsonify
from blockchain import Blockchain

# Chaves privadas e públicas para o blockchain
PRIVATE_KEY = "f6c93994817fddff529c65f477b6631e8a5e64454e0eb903f4f5bb191e2c84f4"
PUBLIC_KEY = "04d7e9ab23c019f17c67b1fd3b1c63ef9e90cf0c1581f5a0123d2e07c8bb82f6f36ad8c5d56b3f6f2fdf0f91b55c6d1705cb3a612b7ed7c6e8c161edcd212cd6d8"

# Inicializa a blockchain
blockchain = Blockchain(PRIVATE_KEY, PUBLIC_KEY)

app = Flask(__name__)

@app.route('/chain', methods=['GET'])
def get_chain():
    """
    Retorna a blockchain completa.
    """
    chain_data = [block.to_dict() for block in blockchain.chain]
    return jsonify(chain_data), 200

@app.route('/validate_block/<int:index>', methods=['GET'])
def validate_block(index):
    """
    Valida um bloco específico da blockchain.
    """
    block = blockchain.get_block(index)
    if not block:
        return jsonify({"message": "Bloco não encontrado"}), 404

    # Valida o bloco comparando o hash e a assinatura
    previous_block = blockchain.get_block(index - 1) if index > 0 else None
    if not block.is_signature_valid(PUBLIC_KEY):
        return jsonify({"message": f"Bloco {index} tem assinatura inválida"}), 400

    if previous_block and block.previous_hash != previous_block.hash:
        return jsonify({"message": f"Bloco {index} tem hash anterior incorreto"}), 400

    if block.hash != block.calculate_hash():
        return jsonify({"message": f"Bloco {index} tem hash inválido"}), 400

    return jsonify({"message": f"Bloco {index} é válido"}), 200

@app.route('/validate_chain', methods=['GET'])
def validate_chain():
    """
    Valida a cadeia inteira.
    """
    if blockchain.is_chain_valid():
        return jsonify({"message": "Blockchain é válida"}), 200
    else:
        return jsonify({"message": "Blockchain é inválida"}), 400

@app.route('/add', methods=['POST'])
def add_block():
    """
    Adiciona um bloco à blockchain.
    """
    data = request.json
    blockchain.add_block(data)
    return jsonify({"message": "Block added!", "data": data}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
