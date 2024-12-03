import os
import paho.mqtt.client as mqtt
import time
import random
import json
import requests
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração MQTT e Blockchain
BROKER = os.getenv("MQTT_HOST_NAME", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))
USER = os.getenv("MQTT_USER_NAME", "user")
PASSWORD = os.getenv("MQTT_PASSWORD", "password")
TOPIC = "iot/data"
BLOCKCHAIN_URL = os.getenv("BLOCKCHAIN_URL", "http://localhost:5000")
DEVICE_ID = os.getenv("HOSTNAME", "iot_device_default")
BR_TZ = pytz.timezone("America/Sao_Paulo")

def generate_data():
    """
    Gera dados simulados para o dispositivo.
    Alterna entre dados válidos e inválidos.
    """
    current_time = datetime.now(BR_TZ).strftime("%Y-%m-%d %H:%M:%S")

    # Alternar entre dados válidos e inválidos
    if random.choice([True, False]):  # 50% de chance para dados válidos
        temperature = round(random.uniform(10, 30), 2)  # Válido
        humidity = round(random.uniform(30, 80), 2)    # Válido
    else:
        temperature = round(random.uniform(0, 50), 2)  # Pode ser inválido
        humidity = round(random.uniform(0, 100), 2)    # Pode ser inválido

    print(f"Gerando dados - Temperatura: {temperature}, Umidade: {humidity}")

    return {
        "device_id": DEVICE_ID,
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": time.time(),
        "formatted_time": current_time
    }

def send_to_blockchain(data):
    """
    Envia os dados para a blockchain via HTTP.
    """
    try:
        response = requests.post(f"{BLOCKCHAIN_URL}/add_data", json=data)
        if response.status_code == 201:
            print(f"Blockchain: Dados adicionados com sucesso: {data}")
        else:
            print(f"Blockchain: Falha ao adicionar dados. Status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Blockchain: Erro ao enviar dados: {e}")

def ensure_device_registered():
    """
    Garante que o dispositivo está registrado antes de enviar dados.
    """
    while True:
        try:
            response = requests.post(f"{BLOCKCHAIN_URL}/add_device", json={"device_id": DEVICE_ID})
            if response.status_code == 201:
                print(f"Dispositivo registrado com sucesso: {DEVICE_ID}")
                break
            else:
                print(f"Falha ao registrar dispositivo: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Erro ao registrar dispositivo: {e}")
        time.sleep(5)  # Aguarde 5 segundos antes de tentar novamente

if __name__ == "__main__":
    # Garantir o registro do dispositivo
    ensure_device_registered()

    # Conectar ao broker MQTT
    client = mqtt.Client()
    client.username_pw_set(USER, PASSWORD)

    try:
        client.connect(BROKER, PORT, 60)
        print(f"Conectado ao Broker MQTT: {BROKER}:{PORT}")

        # Loop de envio de dados e publicação
        while True:
            data = generate_data()
            payload = json.dumps(data)

            # Enviar dados para a blockchain
            send_to_blockchain(data)

            # Publicar dados no MQTT
            client.publish(TOPIC, payload)
            print(f"MQTT: Dados publicados no tópico {TOPIC}: {payload}")

            # Espera entre 1 e 10 segundos
            time.sleep(random.randint(1, 10))

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.disconnect()
        print("Desconectado do Broker MQTT")
