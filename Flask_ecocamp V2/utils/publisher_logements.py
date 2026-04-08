import json
import logging
import MySQLdb
import paho.mqtt.client as mqtt
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

class LogementPublisher:
    def __init__(self):
        # 1. Chargement de la configuration depuis le fichier config.cfg
        self.config = self._load_config()
        
        # 2. Paramètres Base de données récupérés de la conf
        self.db_config = {
            'host': self.config.get("MYSQL_HOST", "172.16.4.102"),
            'user': self.config.get("MYSQL_USER", "ecocamp"),
            'passwd': self.config.get("MYSQL_PASSWORD", "U3TPwTGusZ3x2NjA"),
            'db': self.config.get("MYSQL_DB", "ecocamp"),
            'charset': "utf8mb4"
        }

        # 3. Paramètres MQTT (Utilise l'IP DB par défaut ou une IP spécifique)
        self.mqtt_host = "172.16.4.31" 
        self.mqtt_port = 1883
        self.mqtt_client_id = "publisher_auto_logements"
        self.topic_template = "ecocamp/tableau_bord/{mac}/{nom}"

    def _load_config(self):
        """Lit le fichier config.cfg en remontant d'un dossier depuis /utils/."""
        config = {}
        # On remonte d'un cran pour sortir de 'utils' et trouver 'instance'
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        conf_path = os.path.join(base_dir, 'instance', 'config.cfg')
        
        if os.path.exists(conf_path):
            with open(conf_path) as f:
                for line in f:
                    if '=' in line:
                        name, value = line.split('=', 1)
                        # Nettoyage des espaces et des guillemets
                        config[name.strip()] = value.strip().strip("'").strip('"')
        return config

    def get_logements(self):
        """Récupère les hébergements ayant une MAC valide."""
        try:
            conn = MySQLdb.connect(**self.db_config)
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            # On ne récupère que les logements avec une adresse MAC renseignée
            cursor.execute("""
                SELECT id_hebergement AS id, nom_hebergement AS nom, adresse_mac AS mac
                FROM hebergement
                WHERE adresse_mac IS NOT NULL AND adresse_mac != ''
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except Exception as e:
            log.error(f"Erreur BDD lors de la récupération des logements : {e}")
            return []

    def publier_tout(self):
        """Lance la publication MQTT pour chaque logement trouvé."""
        logements = self.get_logements()
        return self.publier_par_logement(logements)

    def publier_par_logement(self, logements):
        """Lance la publication MQTT pour une liste de logements donnée."""
        if not logements:
            log.warning("Aucun logement fourni.")
            return 0

        # Connexion au Broker MQTT (API v2)
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=self.mqtt_client_id)
        
        try:
            client.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
            client.loop_start()

            for log_data in logements:
                # Nettoyage du nom pour le topic
                nom_clean = log_data['nom'].replace(" ", "_").lower()
                topic = self.topic_template.format(mac=log_data['mac'], nom=nom_clean)
                
                payload = {
                    "id": log_data['id'],
                    "nom": log_data['nom'],
                    "mac": log_data['mac'],
                    "status": "online"
                }

                log.info(f"Publication MQTT -> {topic}")
                client.publish(topic, json.dumps(payload, ensure_ascii=False), qos=1, retain=True)

            client.loop_stop()
            client.disconnect()
            return len(logements)
        except Exception as e:
            log.error(f"Erreur MQTT : {e}")
            raise e

# Permet de tester le script seul en ligne de commande
if __name__ == "__main__":
    pub = LogementPublisher()
    pub.publier_tout()