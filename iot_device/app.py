import os
import paho.mqtt.client as mqtt
import time
import random
import json
import requests
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

BROKER = os.getenv("MQTT_HOST_NAME", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))
USER = os.getenv("MQTT_USER_NAME", "user")
PASSWORD = os.getenv("MQTT_PASSWORD", "password")
TOPIC = "iot/data"
BLOCKCHAIN_URL = os.getenv("BLOCKCHAIN_URL", "http://localhost:5000/add")
DEVICE_ID = os.getenv("HOSTNAME", "iot_device_default")
BR_TZ = pytz.timezone("America/Sao_Paulo")

def generate_data():
    current_time = datetime.now(BR_TZ).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "device_id": DEVICE_ID,
        "temperature": round(random.uniform(20, 30), 2),
        "humidity": round(random.uniform(30, 50), 2),
        "timestamp": time.time(),
        "formatted_time": current_time
    }

def send_to_blockchain(data):
    try:
        response = requests.post(BLOCKCHAIN_URL, json=data)
        if response.status_code == 201:
            print(f"Blockchain: Dados adicionados com sucesso: {data}")
        else:
            print(f"Blockchain: Falha ao adicionar dados. Status: {response.status_code}")
    except Exception as e:
        print(f"Blockchain: Erro ao enviar dados: {e}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.username_pw_set(USER, PASSWORD)

    try:
        client.connect(BROKER, PORT, 60)
        print(f"Conectado ao Broker MQTT: {BROKER}:{PORT}")

        while True:
            data = generate_data()
            payload = json.dumps(data)
            send_to_blockchain(data)
            client.publish(TOPIC, payload)
            print(f"Publicado no MQTT: {payload}")
            time.sleep(random.randint(1, 10))

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client.disconnect()
        print("Desconectado do Broker MQTT")
