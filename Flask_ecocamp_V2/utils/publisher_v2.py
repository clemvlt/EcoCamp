from contextlib import closing
import json
import MySQLdb
from utils.publisher_base import BasePublisher, log


class MessagesPublisher(BasePublisher):
    def __init__(self):
        super().__init__(
            mqtt_client_id="publisher_auto_messages",
            topic_template="ecocamp/tableau_bord/messages",
        )

    def get_messages_actifs(self):
        try:
            with closing(MySQLdb.connect(**self.db_config)) as conn:
                with closing(conn.cursor(MySQLdb.cursors.DictCursor)) as cursor:

                    cursor.execute(
                        """
                        SELECT
                            m.id_message AS id_message,
                            m.contenu_message AS contenu,
                            m.date_debut_message AS date_debut,
                            m.date_fin_message AS date_fin,
                            m.horaire_evenement_message AS horaire,
                            tm.nom_type_message AS type_message
                        FROM message m
                        INNER JOIN type_message tm ON tm.id_type_message = m.id_type_message
                        WHERE CURDATE() BETWEEN m.date_debut_message AND m.date_fin_message
                        ORDER BY m.date_debut_message
                        """
                    )
                    messages = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT
                            h.id_hebergement AS id,
                            h.nom_hebergement AS nom,
                            h.adresse_mac AS mac,
                            tl.nom_type AS type_logement,
                            tl.quota_eau_max AS quota_eau_max,
                            tl.quota_elec_max AS quota_electricite_max,
                            COALESCE(q.eau_quota, tl.quota_eau_max) AS quota_eau,
                            COALESCE(q.electicite_quota, tl.quota_elec_max) AS quota_electricite,
                            eau.index_consommation AS conso_eau,
                            DATE(eau.date_consommation) AS date_conso_eau,
                            elec.index_consommation AS conso_electricite,
                            DATE(elec.date_consommation) AS date_conso_electricite
                        FROM hebergement h
                        LEFT JOIN type_logement tl
                            ON tl.id_type_logement = h.id_type_logement
                        LEFT JOIN sejour s
                            ON s.id_hebergement = h.id_hebergement
                            AND NOW() BETWEEN s.date_debut_sejour AND s.date_fin_sejour
                        LEFT JOIN quota q
                            ON q.id_sejour = s.id_sejour
                        LEFT JOIN consommation eau
                            ON eau.id_hebergement = h.id_hebergement
                            AND eau.id_type_flux = 4
                            AND eau.date_consommation = (
                                SELECT MAX(c.date_consommation)
                                FROM consommation c
                                WHERE c.id_hebergement = h.id_hebergement
                                  AND c.id_type_flux = 4
                            )
                        LEFT JOIN consommation elec
                            ON elec.id_hebergement = h.id_hebergement
                            AND elec.id_type_flux = 3
                            AND elec.date_consommation = (
                                SELECT MAX(c.date_consommation)
                                FROM consommation c
                                WHERE c.id_hebergement = h.id_hebergement
                                  AND c.id_type_flux = 3
                            )
                        WHERE h.adresse_mac IS NOT NULL AND h.adresse_mac != ''
                        """
                    )
                    hebergements = cursor.fetchall()
                    return hebergements, messages

        except Exception as exc:
            log.error("Erreur BDD lors de la recuperation des messages : %s", exc)
            return [], []

    def publier_tout(self):
        hebergements, messages = self.get_messages_actifs()
        self.publier_messages(messages)
        self.publier_infos_hebergements(hebergements)

    # ------------------------------------------------------------------
    # Topic fixe : ecocamp/tableau_bord/messages
    # ------------------------------------------------------------------

    def publier_messages(self, messages):
        messages_payload = [
            {
                "id_message":   row["id_message"],
                "contenu":      row["contenu"],
                "type_message": row["type_message"],
                "date_debut":   row.get("date_debut"),
                "date_fin":     row.get("date_fin"),
                "horaire":      row.get("horaire"),
            }
            for row in messages
        ]

        client = self._create_client()
        try:
            client.connect(self.mqtt_host, self.mqtt_port, keepalive=self.mqtt_keepalive)
            client.loop_start()
            result = client.publish(
                "ecocamp/tableau_bord/messages",
                json.dumps(
                    {"nb_messages": len(messages_payload), "messages": messages_payload},
                    ensure_ascii=False,
                    default=str,
                ),
                qos=1,
                retain=True,
            )
            result.wait_for_publish()
            log.info("Publication MQTT messages -> ecocamp/tableau_bord/messages")
        except Exception as exc:
            log.error("Erreur MQTT messages : %s", exc)
            raise
        finally:
            try:
                client.loop_stop()
            finally:
                client.disconnect()

    # ------------------------------------------------------------------
    # Topic par hébergement : ecocamp/tableau_bord/{mac}/infos_hebergements
    # ------------------------------------------------------------------

    def publier_infos_hebergements(self, hebergements):
        client = self._create_client()
        try:
            client.connect(self.mqtt_host, self.mqtt_port, keepalive=self.mqtt_keepalive)
            client.loop_start()
            for heb in hebergements:
                topic = f"ecocamp/tableau_bord/{heb['mac']}/infos_hebergements"
                payload = {
                    "nom":                    heb["nom"],
                    "type_logement":          heb.get("type_logement"),
                    "quota_eau":              heb.get("quota_eau"),
                    "quota_electricite":      heb.get("quota_electricite"),

                }
                result = client.publish(
                    topic,
                    json.dumps(payload, ensure_ascii=False, default=str),
                    qos=1,
                    retain=True,
                )
                result.wait_for_publish()
                log.info("Publication MQTT infos_hebergements -> %s", topic)
        except Exception as exc:
            log.error("Erreur MQTT infos_hebergements : %s", exc)
            raise
        finally:
            try:
                client.loop_stop()
            finally:
                client.disconnect()


if __name__ == "__main__":
    pub = MessagesPublisher()
    pub.publier_tout()