import hashlib
import time
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import json

class Block:
    def __init__(self, index, data, previous_hash, private_key):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.signature = self.sign_block(private_key)

    def calculate_hash(self):
        """
        Gera o hash do bloco usando seus atributos.
        """
        block_content = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_content.encode()).hexdigest()

    def sign_block(self, private_key):
        """
        Assina o hash do bloco usando a chave privada.
        """
        sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        return sk.sign(self.hash.encode()).hex()

    def is_signature_valid(self, public_key):
        """
        Verifica se a assinatura do bloco é válida.
        """
        vk = VerifyingKey.from_string(bytes.fromhex(public_key), curve=SECP256k1)
        try:
            return vk.verify(bytes.fromhex(self.signature), self.hash.encode())
        except Exception:
            return False

    def to_dict(self):
        """
        Converte o bloco para um dicionário para fácil serialização.
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "signature": self.signature,
        }

    def __str__(self):
        """
        Retorna uma representação legível do bloco.
        """
        return json.dumps(self.to_dict(), indent=4)

class Blockchain:
    def __init__(self, private_key, public_key):
        self.chain = [self.create_genesis_block(private_key)]
        self.private_key = private_key
        self.public_key = public_key

    def create_genesis_block(self, private_key):
        """
        Cria o primeiro bloco (bloco gênese) da cadeia.
        """
        return Block(0, "Genesis Block", "0", private_key)

    def add_block(self, data):
        """
        Adiciona um novo bloco à cadeia.
        """
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), data, previous_block.hash, self.private_key)
        self.chain.append(new_block)

    def is_chain_valid(self):
        """
        Verifica a integridade da cadeia inteira.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Verifica o hash atual
            if current_block.hash != current_block.calculate_hash():
                return False

            # Verifica o hash anterior
            if current_block.previous_hash != previous_block.hash:
                return False

            # Verifica a assinatura do bloco
            if not current_block.is_signature_valid(self.public_key):
                return False

        return True

    def to_json(self):
        """
        Converte toda a blockchain para JSON.
        """
        return json.dumps([block.to_dict() for block in self.chain], indent=4)

    def get_block(self, index):
        """
        Retorna um bloco específico pelo índice.
        """
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None

    def __str__(self):
        """
        Retorna uma representação legível da blockchain.
        """
        return self.to_json()
