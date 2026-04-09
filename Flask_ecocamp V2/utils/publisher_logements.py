from utils.publisher_base import BasePublisher


class LogementPublisher(BasePublisher):
    def __init__(self):
        super().__init__(
            mqtt_client_id="publisher_auto_logements",
            topic_template="ecocamp/tableau_bord/{mac}/nom_hebergement/{nom}",
        )

    def get_logements(self):
        """Recupere les hebergements ayant une MAC valide, avec leur type."""
        return self._query_all(
            """
            SELECT
                h.id_hebergement AS id,
                h.nom_hebergement AS nom,
                h.adresse_mac AS mac,
                tl.nom_type AS type_logement
            FROM hebergement h
            LEFT JOIN type_logement tl ON tl.id_type_logement = h.id_type_logement
            WHERE h.adresse_mac IS NOT NULL AND h.adresse_mac != ''
            """
        )

    def publier_tout(self):
        return self.publier_par_logement(self.get_logements())

    def publier_par_logement(self, logements):
        return self.publish_rows(
            logements,
            payload_builder=lambda logement: {
                "id": logement["id"],
                "nom": logement["nom"],
                "mac": logement["mac"],
                "type_logement": logement.get("type_logement"),
                "status": "online",
            },
            empty_message="Aucun logement fourni.",
            log_label="logement",
        )


if __name__ == "__main__":
    pub = LogementPublisher()
    pub.publier_tout()
