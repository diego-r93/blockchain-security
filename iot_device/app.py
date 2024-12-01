import os
import paho.mqtt.client as mqtt
import time
import random
import json
import requests
from datetime import datetime
import pytz  # Para gerenciar fusos horários
from dotenv import load_dotenv  # Biblioteca para carregar o .env

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do MQTT e Blockchain a partir do .env
BROKER = os.getenv("MQTT_HOST_NAME", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))
USER = os.getenv("MQTT_USER_NAME", "user")
PASSWORD = os.getenv("MQTT_PASSWORD", "password")
TOPIC = "iot/data"
BLOCKCHAIN_URL = os.getenv("BLOCKCHAIN_URL", "http://localhost:5000/add")

# Identificador único do dispositivo (usando o nome do contêiner)
DEVICE_ID = os.getenv("HOSTNAME", "iot_device_default")

# Fuso horário do Brasil
BR_TZ = pytz.timezone("America/Sao_Paulo")

def generate_data():
    """
    Gera dados aleatórios para simular um dispositivo IoT.
    - Temperatura e umidade têm sempre 2 casas decimais.
    """
    current_time = datetime.now(BR_TZ).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "device_id": DEVICE_ID,
        "temperature": round(random.uniform(20, 30), 2),  # Temperatura com 2 casas decimais
        "humidity": round(random.uniform(30, 50), 2),     # Umidade com 2 casas decimais
        "timestamp": time.time(),
        "formatted_time": current_time  # Horário formatado no Brasil
    }

def send_to_blockchain(data):
    """
    Envia os dados gerados para a rede blockchain.
    """
    try:
        response = requests.post(BLOCKCHAIN_URL, json=data)
        if response.status_code == 201:
            print(f"Blockchain: Dados adicionados com sucesso: {data}")
        else:
            print(f"Blockchain: Falha ao adicionar dados. Status: {response.status_code}")
    except Exception as e:
        print(f"Blockchain: Erro ao enviar dados: {e}")

if __name__ == "__main__":
    # Configura MQTT
    client = mqtt.Client()
    client.username_pw_set(USER, PASSWORD)

    try:
        client.connect(BROKER, PORT, 60)
        print(f"Conectado ao Broker MQTT: {BROKER}:{PORT}")

        while True:
            # Gera os dados
            data = generate_data()
            payload = json.dumps(data)

            # Envia para a Blockchain
            send_to_blockchain(data)

            # Publica no Broker MQTT
            client.publish(TOPIC, payload)
            print(f"Publicado no MQTT: {payload}")

            # Tempo aleatório entre 1 e 10 segundos para o próximo envio
            sleep_time = random.randint(1, 10)
            print(f"Aguardando {sleep_time} segundos para o próximo envio...")
            time.sleep(sleep_time)

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.disconnect()
        print("Desconectado do Broker MQTT")
