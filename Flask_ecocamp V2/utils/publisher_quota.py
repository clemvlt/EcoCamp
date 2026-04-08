import json
import logging
import MySQLdb
import paho.mqtt.client as mqtt
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

class QuotaPublisher:
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
        self.mqtt_client_id = "publisher_auto_quota"
        self.topic_template = "ecocamp/tableau_bord/{mac}/{nom}/quota"

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

    def get_quotas(self):
        """
        Récupère les quotas des séjours en cours + consommation actuelle.
        - quota lié à sejour (eau_quota, electicite_quota)
        - consommation actuelle depuis la table consommation (dernier index connu)
        - quota max par type de logement depuis type_logement
        """
        try:
            conn = MySQLdb.connect(**self.db_config)
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("""
                SELECT
                    h.id_hebergement                AS id,
                    h.nom_hebergement               AS nom,
                    h.adresse_mac                   AS mac,
                    s.id_sejour                     AS id_sejour,
                    s.date_debut_sejour             AS date_debut,
                    s.date_fin_sejour               AS date_fin,
                    q.eau_quota                     AS quota_eau,
                    q.electicite_quota              AS quota_electricite,
                    tl.quota_eau_max                AS quota_eau_max,
                    tl.quota_elec_max               AS quota_elec_max,
                    eau.index_consommation          AS conso_eau,
                    elec.index_consommation         AS conso_electricite
                FROM hebergement h
                INNER JOIN sejour s
                    ON s.id_hebergement = h.id_hebergement
                    AND NOW() BETWEEN s.date_debut_sejour AND s.date_fin_sejour
                LEFT JOIN quota q
                    ON q.id_sejour = s.id_sejour
                LEFT JOIN type_logement tl
                    ON tl.id_type_logement = h.id_type_logement
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
            log.error(f"Erreur BDD lors de la récupération des quotas : {e}")
            return []

    def publier_tout(self):
        quotas = self.get_quotas()
        return self.publier_par_quota(quotas)

    def publier_par_quota(self, quotas):
        if not quotas:
            log.warning("Aucun quota à publier (aucun séjour en cours ?).")
            return 0

        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.mqtt_client_id
        )

        try:
            client.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
            client.loop_start()

            for row in quotas:
                nom_clean = row['nom'].replace(" ", "_").lower()
                topic = self.topic_template.format(mac=row['mac'], nom=nom_clean)

                # Pourcentage consommé par rapport au quota défini
                pct_eau = None
                if row.get('quota_eau') and row['quota_eau'] > 0:
                    pct_eau = round((row.get('conso_eau') or 0) / row['quota_eau'] * 100, 2)

                pct_elec = None
                if row.get('quota_electricite') and row['quota_electricite'] > 0:
                    pct_elec = round((row.get('conso_electricite') or 0) / row['quota_electricite'] * 100, 2)

                payload = {
                    "id":                   row['id'],
                    "nom":                  row['nom'],
                    "mac":                  row['mac'],
                    "id_sejour":            row['id_sejour'],
                    "date_debut":           str(row['date_debut']) if row.get('date_debut') else None,
                    "date_fin":             str(row['date_fin']) if row.get('date_fin') else None,
                    # Quota eau
                    "quota_eau":            row.get('quota_eau'),
                    "quota_eau_max":        row.get('quota_eau_max'),
                    "conso_eau":            row.get('conso_eau'),
                    "pct_eau":              pct_eau,
                    # Quota électricité
                    "quota_electricite":    row.get('quota_electricite'),
                    "quota_elec_max":       row.get('quota_elec_max'),
                    "conso_electricite":    row.get('conso_electricite'),
                    "pct_electricite":      pct_elec,
                }

                log.info(f"Publication MQTT quota -> {topic}")
                client.publish(topic, json.dumps(payload, ensure_ascii=False), qos=1, retain=True)

            client.loop_stop()
            client.disconnect()
            return len(quotas)
        except Exception as e:
            log.error(f"Erreur MQTT (quota) : {e}")
            raise e


if __name__ == "__main__":
    pub = QuotaPublisher()
    pub.publier_tout()