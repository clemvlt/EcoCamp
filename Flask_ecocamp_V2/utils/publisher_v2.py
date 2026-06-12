import json
import logging
import os
import re
from contextlib import closing

import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ==============================================================================
# BASE
# ==============================================================================

class BasePublisher:
    def __init__(self, mqtt_client_id, topic_template=None):
        self.config = self._load_config()
        self.db_config = {
            "host":    self.config.get("MYSQL_HOST",     "172.16.4.102"),
            "port":    int(self.config.get("MYSQL_PORT", 3306)),
            "user":    self.config.get("MYSQL_USER",     "ecocamp"),
            "passwd":  self.config.get("MYSQL_PASSWORD", "U3TPwTGusZ3x2NjA"),
            "db":      self.config.get("MYSQL_DB",       "ecocamp"),
            "charset": "utf8mb4",
        }
        self.mqtt_host      = self.config.get("MQTT_HOST",          "172.16.4.102")
        self.mqtt_port      = int(self.config.get("MQTT_PORT",      1883))
        self.mqtt_keepalive = int(self.config.get("MQTT_KEEPALIVE", 60))
        self.mqtt_client_id = mqtt_client_id
        self.topic_template = topic_template

    def _load_config(self):
        config = {}
        base_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        conf_path = os.path.join(base_dir, "instance", "config.cfg")
        if not os.path.exists(conf_path):
            log.warning("Fichier de configuration introuvable : %s", conf_path)
            return config
        with open(conf_path, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip().strip("'").strip('"')
        return config

    def _query_all(self, query, params=None):
        try:
            with closing(MySQLdb.connect(**self.db_config)) as conn:
                with closing(conn.cursor(MySQLdb.cursors.DictCursor)) as cursor:
                    cursor.execute(query, params or {})
                    return cursor.fetchall()
        except Exception as exc:
            log.error("Erreur BDD : %s", exc)
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

    def publish_single(self, topic, payload):
        """Publie un seul message sur un topic fixe."""
        client = self._create_client()
        try:
            client.connect(self.mqtt_host, self.mqtt_port, keepalive=self.mqtt_keepalive)
            client.loop_start()
            result = client.publish(
                topic,
                json.dumps(payload, ensure_ascii=False, default=str),
                qos=1,
                retain=True,
            )
            result.wait_for_publish()
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"Echec publication MQTT sur {topic} (code={result.rc})")
            log.info("Publication MQTT -> %s", topic)
        except Exception as exc:
            log.error("Erreur MQTT (publish_single) : %s", exc)
            raise
        finally:
            try:
                client.loop_stop()
            finally:
                client.disconnect()

    def publish_rows(self, rows, payload_builder, empty_message, log_label):
        """Connecte une fois, publie un message par row."""
        if not rows:
            log.warning(empty_message)
            return 0
        client = self._create_client()
        published = 0
        try:
            client.connect(self.mqtt_host, self.mqtt_port, keepalive=self.mqtt_keepalive)
            client.loop_start()
            for row in rows:
                topic   = self.build_topic(row["mac"], row["nom"])
                payload = payload_builder(row)
                result  = client.publish(
                    topic,
                    json.dumps(payload, ensure_ascii=False, default=str),
                    qos=1,
                    retain=True,
                )
                result.wait_for_publish()
                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    raise RuntimeError(f"Echec publication MQTT sur {topic} (code={result.rc})")
                log.info("Publication MQTT %s -> %s", log_label, topic)
                published += 1
            return published
        except Exception as exc:
            log.error("Erreur MQTT (%s) : %s", log_label, exc)
            raise
        finally:
            try:
                client.loop_stop()
            finally:
                client.disconnect()


# ==============================================================================
# LOGEMENTS
# ==============================================================================

class LogementPublisher(BasePublisher):
    """
    Topic : ecocamp/tableau_bord/{mac}/nom_hebergement/{nom}
    """
    def __init__(self):
        super().__init__(
            mqtt_client_id="publisher_auto_logements",
            topic_template="ecocamp/tableau_bord/{mac}/nom_hebergement/{nom}",
        )

    def publier_tout(self):
        rows = self._query_all(
            """
            SELECT
                h.id_hebergement  AS id,
                h.nom_hebergement AS nom,
                h.adresse_mac     AS mac,
                tl.nom_type       AS type_logement
            FROM hebergement h
            LEFT JOIN type_logement tl ON tl.id_type_logement = h.id_type_logement
            WHERE h.adresse_mac IS NOT NULL AND h.adresse_mac != ''
            """
        )
        self.publish_rows(
            rows,
            payload_builder=lambda row: {
                "id":            row["id"],
                "nom":           row["nom"],
                "mac":           row["mac"],
                "type_logement": row.get("type_logement"),
                "status":        "online",
            },
            empty_message="Aucun logement avec MAC trouvé.",
            log_label="logement",
        )


# ==============================================================================
# CONSOMMATIONS
# ==============================================================================

class ConsommationsPublisher(BasePublisher):
    """
    Topic : ecocamp/tableau_bord/{mac}/consommations_hebergements
    """
    def __init__(self):
        super().__init__(
            mqtt_client_id="publisher_auto_consommations",
            topic_template="ecocamp/tableau_bord/{mac}/consommations_hebergements",
        )

    def _get_data(self):
        return self._query_all(
            """
            SELECT
                h.id_hebergement  AS id,
                h.nom_hebergement AS nom,
                h.adresse_mac     AS mac,

                eau_n.index_consommation AS index_eau,
                eau_n.date_consommation  AS date_eau,
                eau_p.index_consommation AS index_eau_precedent,
                eau_p.date_consommation  AS date_eau_precedent,

                elec_n.index_consommation AS index_electricite,
                elec_n.date_consommation  AS date_electricite,
                elec_p.index_consommation AS index_electricite_precedent,
                elec_p.date_consommation  AS date_electricite_precedent

            FROM hebergement h

            LEFT JOIN consommation eau_n
                ON  eau_n.id_hebergement    = h.id_hebergement AND eau_n.id_type_flux = 4
                AND eau_n.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 4)

            LEFT JOIN consommation eau_p
                ON  eau_p.id_hebergement    = h.id_hebergement AND eau_p.id_type_flux = 4
                AND eau_p.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 4
                      AND c.date_consommation < (
                          SELECT MAX(c2.date_consommation) FROM consommation c2
                          WHERE c2.id_hebergement = h.id_hebergement AND c2.id_type_flux = 4))

            LEFT JOIN consommation elec_n
                ON  elec_n.id_hebergement    = h.id_hebergement AND elec_n.id_type_flux = 3
                AND elec_n.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 3)

            LEFT JOIN consommation elec_p
                ON  elec_p.id_hebergement    = h.id_hebergement AND elec_p.id_type_flux = 3
                AND elec_p.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 3
                      AND c.date_consommation < (
                          SELECT MAX(c2.date_consommation) FROM consommation c2
                          WHERE c2.id_hebergement = h.id_hebergement AND c2.id_type_flux = 3))

            WHERE h.adresse_mac IS NOT NULL AND h.adresse_mac != ''
            """
        )

    def _get_historique_7jours(self, id_hebergement):
        query = """
            SELECT
                jours.jour AS date,
                ROUND(
                    MAX(CASE WHEN c_eau.id_type_flux = 4 THEN c_eau.index_consommation END)
                    - COALESCE(
                        (SELECT c_prev.index_consommation FROM consommation c_prev
                         WHERE c_prev.id_hebergement = %(id)s AND c_prev.id_type_flux = 4
                           AND c_prev.date_consommation < jours.jour
                         ORDER BY c_prev.date_consommation DESC LIMIT 1),
                        (SELECT hc.eau_historique_consommation
                         FROM historique_consommation hc JOIN sejour s ON s.id_sejour = hc.id_sejour
                         WHERE s.id_hebergement = %(id)s
                           AND s.date_debut_sejour <= jours.jour AND s.date_fin_sejour >= jours.jour
                         ORDER BY hc.id_historique_consommation ASC LIMIT 1)
                    ), 3) AS eau_L,
                ROUND(
                    MAX(CASE WHEN c_elec.id_type_flux = 3 THEN c_elec.index_consommation END)
                    - COALESCE(
                        (SELECT c_prev.index_consommation FROM consommation c_prev
                         WHERE c_prev.id_hebergement = %(id)s AND c_prev.id_type_flux = 3
                           AND c_prev.date_consommation < jours.jour
                         ORDER BY c_prev.date_consommation DESC LIMIT 1),
                        (SELECT hc.electricite_historique_consommation
                         FROM historique_consommation hc JOIN sejour s ON s.id_sejour = hc.id_sejour
                         WHERE s.id_hebergement = %(id)s
                           AND s.date_debut_sejour <= jours.jour AND s.date_fin_sejour >= jours.jour
                         ORDER BY hc.id_historique_consommation ASC LIMIT 1)
                    ), 3) AS electricite_kWh
            FROM (
                SELECT CURDATE() - INTERVAL n DAY AS jour
                FROM (SELECT 0 AS n UNION SELECT 1 UNION SELECT 2
                      UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6) seq
            ) jours
            LEFT JOIN consommation c_eau
                ON c_eau.id_hebergement = %(id)s AND c_eau.id_type_flux = 4
                AND DATE(c_eau.date_consommation) = jours.jour
            LEFT JOIN consommation c_elec
                ON c_elec.id_hebergement = %(id)s AND c_elec.id_type_flux = 3
                AND DATE(c_elec.date_consommation) = jours.jour
            GROUP BY jours.jour ORDER BY jours.jour ASC
        """
        try:
            with closing(MySQLdb.connect(**self.db_config)) as conn:
                with closing(conn.cursor(MySQLdb.cursors.DictCursor)) as cursor:
                    cursor.execute(query, {"id": id_hebergement})
                    rows = cursor.fetchall()
        except Exception as exc:
            log.error("Erreur BDD historique 7j (hebergement %s) : %s", id_hebergement, exc)
            return []
        return [
            {
                "date":            str(row["date"]),
                "eau_L":           float(row["eau_L"])           if row.get("eau_L")           is not None and row["eau_L"]           >= 0 else None,
                "electricite_kWh": float(row["electricite_kWh"]) if row.get("electricite_kWh") is not None and row["electricite_kWh"] >= 0 else None,
            }
            for row in rows
        ]

    @staticmethod
    def _diff(a, b):
        if a is None or b is None:
            return None
        d = round(float(a) - float(b), 3)
        return d if d >= 0 else None

    def _build_payload(self, row):
        return {
            "id":  row["id"],
            "nom": row["nom"],
            "mac": row["mac"],
            "index_eau":                       row.get("index_eau"),
            "date_eau":                        row.get("date_eau"),
            "index_eau_precedent":             row.get("index_eau_precedent"),
            "date_eau_precedent":              row.get("date_eau_precedent"),
            "diff_eau":                        self._diff(row.get("index_eau"), row.get("index_eau_precedent")),
            "index_electricite":               row.get("index_electricite"),
            "date_electricite":                row.get("date_electricite"),
            "index_electricite_precedent":     row.get("index_electricite_precedent"),
            "date_electricite_precedent":      row.get("date_electricite_precedent"),
            "diff_electricite":                self._diff(row.get("index_electricite"), row.get("index_electricite_precedent")),
            "historique_7j":                   self._get_historique_7jours(row["id"]),
        }

    def publier_tout(self):
        rows = self._get_data()
        self.publish_rows(rows, self._build_payload, "Aucun hébergement avec MAC trouvé.", "consommations")


# ==============================================================================
# DONNEES
# ==============================================================================

class DonneesPublisher(ConsommationsPublisher):
    """
    Même données que ConsommationsPublisher, topic différent.
    Topic : ecocamp/tableau_bord/{mac}/nom_hebergement/{nom}/donnees
    """
    def __init__(self):
        BasePublisher.__init__(
            self,
            mqtt_client_id="publisher_auto_donnees",
            topic_template="ecocamp/tableau_bord/{mac}/nom_hebergement/{nom}/donnees",
        )

    def publier_tout(self):
        rows = self._get_data()
        self.publish_rows(rows, self._build_payload, "Aucun hébergement avec MAC trouvé.", "donnees")


# ==============================================================================
# QUOTAS
# ==============================================================================

class QuotaPublisher(BasePublisher):
    """
    Topic : ecocamp/tableau_bord/{mac}/nom_hebergement/{nom}/quota
    """
    def __init__(self):
        super().__init__(
            mqtt_client_id="publisher_auto_quota",
            topic_template="ecocamp/tableau_bord/{mac}/nom_hebergement/{nom}/quota",
        )

    def publier_tout(self):
        rows = self._query_all(
            """
            SELECT
                h.id_hebergement  AS id,
                h.nom_hebergement AS nom,
                h.adresse_mac     AS mac,
                tl.nom_type       AS type_logement,
                s.id_sejour, s.date_debut_sejour AS date_debut, s.date_fin_sejour AS date_fin,
                q.eau_quota AS quota_eau_sejour, q.electicite_quota AS quota_electricite_sejour,
                tl.quota_eau_max, tl.quota_elec_max,
                eau.index_consommation  AS conso_eau,  eau.date_consommation  AS date_conso_eau,
                elec.index_consommation AS conso_electricite, elec.date_consommation AS date_conso_electricite
            FROM hebergement h
            LEFT JOIN type_logement tl ON tl.id_type_logement = h.id_type_logement
            LEFT JOIN sejour s ON s.id_hebergement = h.id_hebergement
                AND NOW() BETWEEN s.date_debut_sejour AND s.date_fin_sejour
            LEFT JOIN quota q ON q.id_sejour = s.id_sejour
            LEFT JOIN consommation eau
                ON eau.id_hebergement = h.id_hebergement AND eau.id_type_flux = 4
                AND eau.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 4)
            LEFT JOIN consommation elec
                ON elec.id_hebergement = h.id_hebergement AND elec.id_type_flux = 3
                AND elec.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 3)
            WHERE h.adresse_mac IS NOT NULL AND h.adresse_mac != ''
            """
        )

        def build_payload(row):
            quota_eau  = row.get("quota_eau_sejour")  or row.get("quota_eau_max")
            quota_elec = row.get("quota_electricite_sejour") or row.get("quota_elec_max")
            pct = lambda c, q: round(float(c) / float(q) * 100, 2) if c is not None and q and q > 0 else None
            return {
                "id": row["id"], "nom": row["nom"], "mac": row["mac"],
                "type_logement":             row.get("type_logement"),
                "sejour_actif":              row.get("id_sejour") is not None,
                "id_sejour":                 row.get("id_sejour"),
                "date_debut":                row.get("date_debut"),
                "date_fin":                  row.get("date_fin"),
                "quota_eau":                 quota_eau,
                "quota_eau_sejour":          row.get("quota_eau_sejour"),
                "quota_eau_max":             row.get("quota_eau_max"),
                "conso_eau":                 row.get("conso_eau"),
                "date_conso_eau":            row.get("date_conso_eau"),
                "pct_eau":                   pct(row.get("conso_eau"), quota_eau),
                "quota_electricite":         quota_elec,
                "quota_electricite_sejour":  row.get("quota_electricite_sejour"),
                "quota_elec_max":            row.get("quota_elec_max"),
                "conso_electricite":         row.get("conso_electricite"),
                "date_conso_electricite":    row.get("date_conso_electricite"),
                "pct_electricite":           pct(row.get("conso_electricite"), quota_elec),
            }

        self.publish_rows(rows, build_payload, "Aucun hébergement avec MAC trouvé.", "quota")


# ==============================================================================
# MESSAGES + INFOS HEBERGEMENTS
# ==============================================================================

class MessagesPublisher(BasePublisher):
    """
    Topic fixe    : ecocamp/tableau_bord/messages  → tous les messages actifs (hors événements)
    Topic par mac : ecocamp/tableau_bord/{mac}/infos_hebergements
    """
    def __init__(self):
        super().__init__(
            mqtt_client_id="publisher_auto_messages",
            topic_template="ecocamp/tableau_bord/{mac}/infos_hebergements",
        )

    def publier_tout(self):
        try:
            with closing(MySQLdb.connect(**self.db_config)) as conn:
                with closing(conn.cursor(MySQLdb.cursors.DictCursor)) as cursor:

                    # Tous les messages actifs aujourd'hui (hors événements)
                    cursor.execute(
                        """
                        SELECT m.id_message, m.contenu_message AS contenu,
                               m.date_debut_message AS date_debut, m.date_fin_message AS date_fin,
                               m.horaire_evenement_message AS horaire,
                               tm.nom_type_message AS type_message
                        FROM message m
                        INNER JOIN type_message tm ON tm.id_type_message = m.id_type_message
                        WHERE CURDATE() BETWEEN m.date_debut_message AND m.date_fin_message
                          AND tm.nom_type_message != 'Evenement'
                        ORDER BY m.id_message ASC
                        """
                    )
                    messages = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT h.id_hebergement AS id, h.nom_hebergement AS nom, h.adresse_mac AS mac,
                               tl.nom_type AS type_logement,
                               COALESCE(q.eau_quota,        tl.quota_eau_max)  AS quota_eau,
                               COALESCE(q.electicite_quota, tl.quota_elec_max) AS quota_electricite
                        FROM hebergement h
                        LEFT JOIN type_logement tl ON tl.id_type_logement = h.id_type_logement
                        LEFT JOIN sejour s ON s.id_hebergement = h.id_hebergement
                            AND NOW() BETWEEN s.date_debut_sejour AND s.date_fin_sejour
                        LEFT JOIN quota q ON q.id_sejour = s.id_sejour
                        WHERE h.adresse_mac IS NOT NULL AND h.adresse_mac != ''
                        """
                    )
                    hebergements = cursor.fetchall()
        except Exception as exc:
            log.error("Erreur BDD (messages) : %s", exc)
            return

        # Topic fixe : tous les messages actifs (hors événements)
        self.publish_single(
            "ecocamp/tableau_bord/messages",
            {
                "nb_messages": len(messages),
                "messages": [
                    {
                        "id_message":   row["id_message"],
                        "contenu":      row["contenu"],
                        "type_message": row["type_message"],
                        "date_debut":   row.get("date_debut"),
                        "date_fin":     row.get("date_fin"),
                    }
                    for row in messages
                ],
            },
        )

        # Topic par hébergement : infos + quotas
        self.publish_rows(
            hebergements,
            payload_builder=lambda heb: {
                "nom":               heb["nom"],
                "type_logement":     heb.get("type_logement"),
                "quota_eau":         heb.get("quota_eau"),
                "quota_electricite": heb.get("quota_electricite"),
            },
            empty_message="Aucun hébergement avec MAC trouvé.",
            log_label="infos_hebergements",
        )


# ==============================================================================
# EVENEMENTS
# ==============================================================================

class EvenementsPublisher(BasePublisher):
    """
    Topic fixe : ecocamp/tableau_bord/evenements → tous les événements actifs
    """
    def __init__(self):
        super().__init__(
            mqtt_client_id="publisher_auto_evenements",
            topic_template=None,  # topic fixe uniquement, pas de publish_rows
        )

    def publier_tout(self):
        try:
            with closing(MySQLdb.connect(**self.db_config)) as conn:
                with closing(conn.cursor(MySQLdb.cursors.DictCursor)) as cursor:
                    cursor.execute(
                        """
                        SELECT m.id_message, m.contenu_message AS contenu,
                               m.date_debut_message AS date_debut, m.date_fin_message AS date_fin,
                               m.horaire_evenement_message AS horaire,
                               tm.nom_type_message AS type_message
                        FROM message m
                        INNER JOIN type_message tm ON tm.id_type_message = m.id_type_message
                        WHERE tm.nom_type_message = 'Evenement'
                          AND CURDATE() BETWEEN m.date_debut_message AND m.date_fin_message
                        ORDER BY m.date_debut_message, m.horaire_evenement_message
                        """
                    )
                    evenements = cursor.fetchall()
        except Exception as exc:
            log.error("Erreur BDD (événements) : %s", exc)
            return

        # Topic fixe uniquement
        self.publish_single(
            "ecocamp/tableau_bord/evenements",
            {
                "nb_evenements": len(evenements),
                "evenements": [
                    {
                        "id_message":   row["id_message"],
                        "contenu":      row["contenu"],
                        "type_message": row["type_message"],
                        "date_debut":   row.get("date_debut"),
                        "date_fin":     row.get("date_fin"),
                        "horaire":      row.get("horaire"),
                    }
                    for row in evenements
                ],
            },
        )


# ==============================================================================
# ORCHESTRATEUR
# ==============================================================================

def main():
    publishers = [
        ("Logements",     LogementPublisher),
        ("Consommations", ConsommationsPublisher),
        ("Donnees",       DonneesPublisher),
        ("Quotas",        QuotaPublisher),
        ("Messages",      MessagesPublisher),
        ("Evenements",    EvenementsPublisher),
    ]

    for label, cls in publishers:
        try:
            log.info("=== Démarrage : %s ===", label)
            cls().publier_tout()
            log.info("=== Terminé   : %s ===", label)
        except Exception as exc:
            log.error("Erreur dans %s : %s", label, exc)


if __name__ == "__main__":
    main()