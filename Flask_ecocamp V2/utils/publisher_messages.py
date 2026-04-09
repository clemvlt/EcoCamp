from contextlib import closing

import MySQLdb

from utils.publisher_base import BasePublisher, log


class MessagesPublisher(BasePublisher):
    def __init__(self):
        super().__init__(
            mqtt_client_id="publisher_auto_messages",
            topic_template="ecocamp/tableau_bord/{mac}/nom_hebergement/{nom}/messages",
        )

    def get_messages_actifs(self):
        """
        Recupere les messages actifs puis les diffuse a tous les hebergements
        ayant une adresse MAC valide.
        """
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
                            id_hebergement AS id,
                            nom_hebergement AS nom,
                            adresse_mac AS mac
                        FROM hebergement
                        WHERE adresse_mac IS NOT NULL AND adresse_mac != ''
                        """
                    )
                    hebergements = cursor.fetchall()
                    return hebergements, messages
        except Exception as exc:
            log.error("Erreur BDD lors de la recuperation des messages : %s", exc)
            return [], []

    def publier_tout(self):
        hebergements, messages = self.get_messages_actifs()
        return self.publier_par_messages(hebergements, messages)

    def publier_par_messages(self, hebergements, messages):
        messages_payload = [
            {
                "id_message": row["id_message"],
                "contenu": row["contenu"],
                "type_message": row["type_message"],
                "date_debut": row.get("date_debut"),
                "date_fin": row.get("date_fin"),
                "horaire": row.get("horaire"),
            }
            for row in messages
        ]

        return self.publish_rows(
            hebergements,
            payload_builder=lambda heb: {
                "id": heb["id"],
                "nom": heb["nom"],
                "mac": heb["mac"],
                "nb_messages": len(messages_payload),
                "messages": messages_payload,
            },
            empty_message="Aucun hebergement a publier.",
            log_label="messages",
        )


if __name__ == "__main__":
    pub = MessagesPublisher()
    pub.publier_tout()
