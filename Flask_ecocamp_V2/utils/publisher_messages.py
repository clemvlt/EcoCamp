# publishers/events_publisher.py

from contextlib import closing
import MySQLdb
from utils.publisher_base import BasePublisher, log


class EventsPublisher(BasePublisher):
    def __init__(self):
        super().__init__(
            mqtt_client_id="publisher_auto_events",
            topic_template="ecocamp/tableau_bord/evenements",
        )

    def get_evenements_actifs(self):
        """
        Récupère les événements actifs (type_message = 'Evenement')
        puis les diffuse à tous les hébergements ayant une adresse MAC valide.
        """
        try:
            with closing(MySQLdb.connect(**self.db_config)) as conn:
                with closing(conn.cursor(MySQLdb.cursors.DictCursor)) as cursor:
                    cursor.execute(
                        """
                        SELECT
                            m.id_message                AS id_message,
                            m.contenu_message           AS contenu,
                            m.date_debut_message        AS date_debut,
                            m.date_fin_message          AS date_fin,
                            m.horaire_evenement_message AS horaire,
                            tm.nom_type_message         AS type_message
                        FROM message m
                        INNER JOIN type_message tm
                            ON tm.id_type_message = m.id_type_message
                        WHERE tm.nom_type_message = 'Evenement'
                          AND CURDATE() BETWEEN m.date_debut_message AND m.date_fin_message
                        ORDER BY m.date_debut_message, m.horaire_evenement_message
                        """
                    )
                    evenements = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT
                            id_hebergement AS id,
                            nom_hebergement AS nom,
                            adresse_mac     AS mac
                        FROM hebergement
                        WHERE adresse_mac IS NOT NULL AND adresse_mac != ''
                        """
                    )
                    hebergements = cursor.fetchall()

            return hebergements, evenements

        except Exception as exc:
            log.error("Erreur BDD lors de la récupération des événements : %s", exc)
            return [], []

    def publier_tout(self):
        hebergements, evenements = self.get_evenements_actifs()
        return self.publier_par_evenements(hebergements, evenements)

    def publier_par_evenements(self, hebergements, evenements):
        evenements_payload = [
            {
                "contenu":      row["contenu"],
                "type_message": row["type_message"],
                "date_debut":   row.get("date_debut"),
                "date_fin":     row.get("date_fin"),
                "horaire":      row.get("horaire"),
            }
            for row in evenements
        ]

        return self.publish_rows(
            hebergements,
            payload_builder=lambda heb: {
                "nom":           heb["nom"],
                "nb_evenements": len(evenements_payload),
                "evenements":    evenements_payload,
            },
            empty_message="Aucun hébergement à publier.",
            log_label="evenements",
        )


if __name__ == "__main__":
    pub = EventsPublisher()
    pub.publier_tout()