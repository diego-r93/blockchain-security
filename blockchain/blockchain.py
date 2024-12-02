import hashlib
import time
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import json

def generate_public_key(private_key_hex):
    sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
    vk = sk.verifying_key
    return vk.to_string().hex()

class Block:
    def __init__(self, index, data, previous_hash, private_key):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.signature = self.sign_block(private_key)

    def calculate_hash(self):
        block_content = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_content.encode()).hexdigest()

    def sign_block(self, private_key):
        sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        return sk.sign(self.hash.encode()).hex()

    def is_signature_valid(self, public_key):
        try:
            vk = VerifyingKey.from_string(bytes.fromhex(public_key), curve=SECP256k1)
            return vk.verify(bytes.fromhex(self.signature), self.hash.encode())
        except Exception as e:
            print(f"Erro na validação da assinatura: {e}")
            return False

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "signature": self.signature,
        }

class Blockchain:
    def __init__(self, private_key, public_key):
        self.chain = [self.create_genesis_block(private_key)]
        self.private_key = private_key
        self.public_key = public_key

    def create_genesis_block(self, private_key):
        return Block(0, "Genesis Block", "0", private_key)

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), data, previous_block.hash, self.private_key)
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

            if not current_block.is_signature_valid(self.public_key):
                return False

        return True
