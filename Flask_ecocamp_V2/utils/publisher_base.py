import json
import logging
import os
import re
from contextlib import closing

import MySQLdb
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


class BasePublisher:
    """Briques communes pour publier vers le broker MQTT puis Node-RED."""

    def __init__(self, mqtt_client_id, topic_template):
        self.config = self._load_config()
        self.db_config = {
            "host": self.config.get("MYSQL_HOST", "172.16.4.102"),
            "port": int(self.config.get("MYSQL_PORT", 3306)),
            "user": self.config.get("MYSQL_USER", "ecocamp"),
            "passwd": self.config.get("MYSQL_PASSWORD", "U3TPwTGusZ3x2NjA"),
            "db": self.config.get("MYSQL_DB", "ecocamp"),
            "charset": "utf8mb4",
        }
        self.mqtt_host = self.config.get("MQTT_HOST", "172.16.4.31")
        self.mqtt_port = int(self.config.get("MQTT_PORT", 1883))
        self.mqtt_keepalive = int(self.config.get("MQTT_KEEPALIVE", 60))
        self.mqtt_client_id = mqtt_client_id
        self.topic_template = topic_template

    def _load_config(self):
        config = {}
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        conf_path = os.path.join(base_dir, "instance", "config.cfg")
        if not os.path.exists(conf_path):
            log.warning("Fichier de configuration introuvable: %s", conf_path)
            return config
        with open(conf_path, encoding="utf-8") as config_file:
            for raw_line in config_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip().strip("'").strip('"')
        return config

    def _query_all(self, query):
        try:
            with closing(MySQLdb.connect(**self.db_config)) as conn:
                with closing(conn.cursor(MySQLdb.cursors.DictCursor)) as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except Exception as exc:
            log.error("Erreur BDD: %s", exc)
            return []

    def _create_client(self):
        return mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.mqtt_client_id,
        )

    def _normalize_topic_segment(self, value):
        normalized = re.sub(r"\s+", "_", (value or "").strip().lower())
        normalized = re.sub(r"[^a-z0-9_-]", "", normalized)
        return normalized or "inconnu"

    def build_topic(self, mac, nom):
        return self.topic_template.format(mac=mac, nom=self._normalize_topic_segment(nom))

    def publish_rows(self, rows, payload_builder, empty_message, log_label):
        if not rows:
            log.warning(empty_message)
            return 0
        client = self._create_client()
        published = 0
        try:
            client.connect(self.mqtt_host, self.mqtt_port, keepalive=self.mqtt_keepalive)
            client.loop_start()
            for row in rows:
                topic = self.build_topic(row["mac"], row["nom"])
                payload = payload_builder(row)
                result = client.publish(
                    topic,
                    json.dumps(payload, ensure_ascii=False, default=str),
                    qos=1,
                    retain=True,
                )
                result.wait_for_publish()
                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    raise RuntimeError(f"Echec de publication MQTT sur {topic} (code={result.rc})")
                log.info("Publication MQTT %s -> %s", log_label, topic)
                published += 1
            return published
        except Exception as exc:
            log.error("Erreur MQTT (%s): %s", log_label, exc)
            raise
        finally:
            try:
                client.loop_stop()
            finally:
                client.disconnect()
