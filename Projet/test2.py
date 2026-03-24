import paho.mqtt.client as mqtt
import pymysql
import json
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

# --------- Déchiffrage de la configuration ---------

def load_encrypted_config():
    password_env = os.getenv("CONFIG_PWD")

    if not password_env:
        print("Erreur : variable CONFIG_PWD introuvable")
        return None

    master_password = password_env.encode()

    try:
        with open("config.enc", "rb") as f:
            file_content = f.read()

        salt = file_content[:16]
        encrypted_data = file_content[16:]

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(master_password))
        fernet = Fernet(key)

        decrypted_data = fernet.decrypt(encrypted_data)

        return json.loads(decrypted_data.decode())

    except Exception as e:
        print("Erreur déchiffrage :", e)
        return None


config = load_encrypted_config()


# --------- Gestion SQL ---------

class Controleur:

    def __init__(self, db_config):
        self.db = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db_name']
        )

    def sauvegarder(self, index, id_type_flux):

        try:
            with self.db.cursor() as cursor:

                sql = """
                INSERT INTO consommation
                (index_consommation, id_sejour, id_type_flux)
                VALUES (%s, 1, %s)
                """

                cursor.execute(sql, (index, id_type_flux))
                self.db.commit()

                print(f"Index {index} enregistré (flux {id_type_flux})")

        except Exception as e:
            print("Erreur SQL :", e)


# --------- Gestion MQTT ---------

class ReceptionDataEau:

    # mapping device → flux
    DEVICE_FLUX = {
        "eau-ecocamp-mq": 4,
    }

    def __init__(self, manager):
        self.manager = manager

    def on_connect(self, client, userdata, flags, rc):

        if rc == 0:
            print("Connecté au broker MQTT")
            client.subscribe(config['mqtt']['topic'])
        else:
            print("Erreur connexion :", rc)

    def on_message(self, client, userdata, msg):

        try:
            data = json.loads(msg.payload.decode())

            dev_id = data.get('end_device_ids', {}).get('device_id')

            uplink = data.get('uplink_message', {})
            payload = uplink.get('decoded_payload', {})

            values = payload.get('bytes', {}).get('counterValues', [])

            if not values:
                return

            index = values[0]

            id_type_flux = self.DEVICE_FLUX.get(dev_id)

            if id_type_flux is None:
                print("Capteur inconnu :", dev_id)
                return

            # délégation au contrôleur SQL
            self.manager.sauvegarder(index, id_type_flux)

        except Exception as e:
            print("Erreur traitement message :", e)

# --------- Lancement ---------

manager = Controleur(config['database'])
receiver = ReceptionDataEau(manager)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

client.username_pw_set(
    config['mqtt']['user'],
    config['mqtt']['password']
)

client.on_connect = receiver.on_connect
client.on_message = receiver.on_message

try:
    client.connect(
        config['mqtt']['broker'],
        config['mqtt']['port'],
        60
    )

    client.loop_forever()

except KeyboardInterrupt:
    print("Arrêt du service")
    client.disconnect()