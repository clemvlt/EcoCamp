import json
import logging
import MySQLdb
import paho.mqtt.client as mqtt
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

class DonneesPublisher:
    def __init__(self):
        self.config = self._load_config()

        self.db_config = {
            'host': self.config.get("MYSQL_HOST", "172.16.4.102"),
            'user': self.config.get("MYSQL_USER", "ecocamp"),
            'passwd': self.config.get("MYSQL_PASSWORD", "U3TPwTGusZ3x2NjA"),
            'db': self.config.get("MYSQL_DB", "ecocamp"),
            'charset': "utf8mb4"
        }

        self.mqtt_host = "172.16.4.31"
        self.mqtt_port = 1883
        self.mqtt_client_id = "publisher_auto_donnees"
        self.topic_template = "ecocamp/tableau_bord/{mac}/{nom}/donnees"

    def _load_config(self):
        config = {}
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        conf_path = os.path.join(base_dir, 'instance', 'config.cfg')
        if os.path.exists(conf_path):
            with open(conf_path) as f:
                for line in f:
                    if '=' in line:
                        name, value = line.split('=', 1)
                        config[name.strip()] = value.strip().strip("'").strip('"')
        return config

    def get_donnees(self):
        """
        Récupère le dernier index de consommation eau (id_type_flux=4)
        et électricité (id_type_flux=3) par hébergement.
        """
        try:
            conn = MySQLdb.connect(**self.db_config)
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("""
                SELECT
                    h.id_hebergement            AS id,
                    h.nom_hebergement           AS nom,
                    h.adresse_mac               AS mac,
                    eau.index_consommation      AS index_eau,
                    eau.date_consommation       AS date_eau,
                    elec.index_consommation     AS index_electricite,
                    elec.date_consommation      AS date_electricite
                FROM hebergement h
                LEFT JOIN consommation eau
                    ON eau.id_hebergement = h.id_hebergement
                    AND eau.id_type_flux = 4
                    AND eau.date_consommation = (
                        SELECT MAX(c2.date_consommation)
                        FROM consommation c2
                        WHERE c2.id_hebergement = h.id_hebergement
                          AND c2.id_type_flux = 4
                    )
                LEFT JOIN consommation elec
                    ON elec.id_hebergement = h.id_hebergement
                    AND elec.id_type_flux = 3
                    AND elec.date_consommation = (
                        SELECT MAX(c3.date_consommation)
                        FROM consommation c3
                        WHERE c3.id_hebergement = h.id_hebergement
                          AND c3.id_type_flux = 3
                    )
                WHERE h.adresse_mac IS NOT NULL AND h.adresse_mac != ''
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except Exception as e:
            log.error(f"Erreur BDD lors de la récupération des données : {e}")
            return []

    def publier_tout(self):
        donnees = self.get_donnees()
        return self.publier_par_donnees(donnees)

    def publier_par_donnees(self, donnees):
        if not donnees:
            log.warning("Aucune donnée de consommation à publier.")
            return 0

        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.mqtt_client_id
        )

        try:
            client.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
            client.loop_start()

            for row in donnees:
                nom_clean = row['nom'].replace(" ", "_").lower()
                topic = self.topic_template.format(mac=row['mac'], nom=nom_clean)

                payload = {
                    "id":                row['id'],
                    "nom":               row['nom'],
                    "mac":               row['mac'],
                    "index_eau":         row.get('index_eau'),
                    "date_eau":          str(row['date_eau']) if row.get('date_eau') else None,
                    "index_electricite": row.get('index_electricite'),
                    "date_electricite":  str(row['date_electricite']) if row.get('date_electricite') else None,
                }

                log.info(f"Publication MQTT donnees -> {topic}")
                client.publish(topic, json.dumps(payload, ensure_ascii=False), qos=1, retain=True)

            client.loop_stop()
            client.disconnect()
            return len(donnees)
        except Exception as e:
            log.error(f"Erreur MQTT (donnees) : {e}")
            raise e


if __name__ == "__main__":
    pub = DonneesPublisher()
    pub.publier_tout()