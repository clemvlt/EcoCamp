import json
import logging
import MySQLdb
import paho.mqtt.client as mqtt
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

class MessagesPublisher:
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
        self.mqtt_client_id = "publisher_auto_messages"
        self.topic_template = "ecocamp/tableau_bord/{mac}/{nom}/messages"

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

    def get_messages_actifs(self):
        """
        Récupère les messages actifs aujourd'hui (entre date_debut_message et date_fin_message).
        Les messages sont globaux (pas liés à un hébergement spécifique),
        donc on les diffuse à tous les hébergements avec une MAC valide.
        """
        try:
            conn = MySQLdb.connect(**self.db_config)
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)

            # Récupère les messages dont la plage de dates est active aujourd'hui
            cursor.execute("""
                SELECT
                    m.id_message                AS id_message,
                    m.contenu_message           AS contenu,
                    m.date_debut_message        AS date_debut,
                    m.date_fin_message          AS date_fin,
                    m.horaire_evenement_message AS horaire,
                    tm.nom_type_message         AS type_message
                FROM message m
                INNER JOIN type_message tm ON tm.id_type_message = m.id_type_message
                WHERE CURDATE() BETWEEN m.date_debut_message AND m.date_fin_message
                ORDER BY m.date_debut_message
            """)
            messages = cursor.fetchall()

            # Récupère tous les hébergements avec MAC valide
            cursor.execute("""
                SELECT id_hebergement AS id, nom_hebergement AS nom, adresse_mac AS mac
                FROM hebergement
                WHERE adresse_mac IS NOT NULL AND adresse_mac != ''
            """)
            hebergements = cursor.fetchall()

            cursor.close()
            conn.close()
            return hebergements, messages
        except Exception as e:
            log.error(f"Erreur BDD lors de la récupération des messages : {e}")
            return [], []

    def publier_tout(self):
        hebergements, messages = self.get_messages_actifs()
        return self.publier_par_messages(hebergements, messages)

    def publier_par_messages(self, hebergements, messages):
        if not hebergements:
            log.warning("Aucun hébergement à publier.")
            return 0

        if not messages:
            log.warning("Aucun message actif aujourd'hui.")

        # Sérialise la liste des messages une seule fois
        messages_payload = [
            {
                "id_message":   row['id_message'],
                "contenu":      row['contenu'],
                "type_message": row['type_message'],
                "date_debut":   str(row['date_debut']) if row.get('date_debut') else None,
                "date_fin":     str(row['date_fin']) if row.get('date_fin') else None,
                "horaire":      str(row['horaire']) if row.get('horaire') else None,
            }
            for row in messages
        ]

        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.mqtt_client_id
        )

        try:
            client.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
            client.loop_start()

            for heb in hebergements:
                nom_clean = heb['nom'].replace(" ", "_").lower()
                topic = self.topic_template.format(mac=heb['mac'], nom=nom_clean)

                payload = {
                    "id":           heb['id'],
                    "nom":          heb['nom'],
                    "mac":          heb['mac'],
                    "nb_messages":  len(messages_payload),
                    "messages":     messages_payload,
                }

                log.info(f"Publication MQTT messages -> {topic} ({len(messages_payload)} msg actifs)")
                client.publish(topic, json.dumps(payload, ensure_ascii=False), qos=1, retain=True)

            client.loop_stop()
            client.disconnect()
            return len(hebergements)
        except Exception as e:
            log.error(f"Erreur MQTT (messages) : {e}")
            raise e


if __name__ == "__main__":
    pub = MessagesPublisher()
    pub.publier_tout()