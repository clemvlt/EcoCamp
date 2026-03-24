import paho.mqtt.client as mqtt
import json
import os

# --- Chargement de la Configuration ---
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
CONF_MQTT = config['mqtt']

class ReceptionDataEau:
    @staticmethod
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connecté avec succès au Broker MQTT")
            client.subscribe(CONF_MQTT['topic'])
            print(f"Abonné au topic : {CONF_MQTT['topic']}")
        else:
            print(f"Échec de connexion, code : {rc}")

    @staticmethod
    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            uplink = data.get('uplink_message', {})
            decoded = uplink.get('decoded_payload', {})
            values = decoded.get('bytes', {}).get('counterValues', [])

            if values:
                # K=1 donc 1 impulsion = 1 litre
                compteur_a = values[0]
                print(f"\n--- Nouvelle Lecture ---")
                print(f"Index Eau : {compteur_a / 1000:.3f} m³ ({compteur_a} L)")
                print(f"Heure    : {data.get('received_at')}")
            else:
                print("Pas de données de compteur dans ce message.")
        except Exception as e:
            print(f"Erreur décodage : {e}")

# --- Initialisation du Client ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.username_pw_set(CONF_MQTT['user'], CONF_MQTT['password'])

# Assigner les callbacks (on pointe vers les méthodes de la classe)
client.on_connect = ReceptionDataEau.on_connect
client.on_message = ReceptionDataEau.on_message

# Connexion
try:
    print(f"Connexion à {CONF_MQTT['broker']}...")
    client.connect(CONF_MQTT['broker'], CONF_MQTT['port'], 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\nArrêt...")
    client.disconnect()