from contextlib import closing
import MySQLdb
from utils.publisher_base import BasePublisher, log


class ConsommationsPublisher(BasePublisher):
    """
    Publie vers le broker MQTT les consommations de chaque hébergement :
      - Index eau / électricité : dernier + avant-dernier + diff
      - Historique des 7 derniers jours
    Topic : ecocamp/tableau_bord/{mac}/consommations_hebergements
    """

    def __init__(self):
        super().__init__(
            mqtt_client_id="publisher_auto_consommations",
            topic_template="ecocamp/tableau_bord/{mac}/consommations_hebergements",
        )

    # ------------------------------------------------------------------
    # Requête principale — index courant + précédent
    # ------------------------------------------------------------------

    def get_consommations(self):
        """Récupère le dernier et avant-dernier index eau + élec pour chaque hébergement."""
        # Requête SQL complexe pour obtenir les index de consommation actuels et précédents
        # pour l'eau (id_type_flux = 4) et l'électricité (id_type_flux = 3)
        return self._query_all(
            """
            SELECT
                h.id_hebergement AS id,
                h.nom_hebergement AS nom,
                h.adresse_mac AS mac,

                eau_n.index_consommation AS index_eau,
                eau_n.date_consommation  AS date_eau,
                eau_p.index_consommation AS index_eau_precedent,
                eau_p.date_consommation  AS date_eau_precedent,

                elec_n.index_consommation AS index_electricite,
                elec_n.date_consommation  AS date_electricite,
                elec_p.index_consommation AS index_electricite_precedent,
                elec_p.date_consommation  AS date_electricite_precedent

            FROM hebergement h

            /* Dernier index eau (id_type_flux = 4) */
            LEFT JOIN consommation eau_n
                ON eau_n.id_hebergement     = h.id_hebergement
                AND eau_n.id_type_flux      = 4
                AND eau_n.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 4
                )

            /* Avant-dernier index eau */
            LEFT JOIN consommation eau_p
                ON eau_p.id_hebergement     = h.id_hebergement
                AND eau_p.id_type_flux      = 4
                AND eau_p.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement  = h.id_hebergement
                      AND c.id_type_flux    = 4
                      AND c.date_consommation < (
                          SELECT MAX(c2.date_consommation) FROM consommation c2
                          WHERE c2.id_hebergement = h.id_hebergement AND c2.id_type_flux = 4
                      )
                )

            /* Dernier index électricité (id_type_flux = 3) */
            LEFT JOIN consommation elec_n
                ON elec_n.id_hebergement     = h.id_hebergement
                AND elec_n.id_type_flux      = 3
                AND elec_n.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 3
                )

            /* Avant-dernier index électricité */
            LEFT JOIN consommation elec_p
                ON elec_p.id_hebergement     = h.id_hebergement
                AND elec_p.id_type_flux      = 3
                AND elec_p.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement  = h.id_hebergement
                      AND c.id_type_flux    = 3
                      AND c.date_consommation < (
                          SELECT MAX(c2.date_consommation) FROM consommation c2
                          WHERE c2.id_hebergement = h.id_hebergement AND c2.id_type_flux = 3
                      )
                )

            WHERE h.adresse_mac IS NOT NULL AND h.adresse_mac != ''
            """
        )

    # ------------------------------------------------------------------
    # Historique 7 jours
    # ------------------------------------------------------------------

    def get_historique_7jours(self, id_hebergement: int) -> list[dict]:
        """
        Calcule la consommation journalière réelle eau + élec sur les 7 derniers jours.
        Formule : MAX(index_J) - dernier index avant J
        Fallback sur l'index de départ du séjour actif si aucun relevé précédent.
        """
        # Requête complexe pour calculer les consommations journalières
        # en soustrayant l'index du jour précédent de l'index du jour actuel
        # Utilise un fallback sur l'historique de consommation du séjour si nécessaire
        query = """
            SELECT
                jours.jour AS date,

                /* Consommation eau du jour = index du jour - index de la veille */
                ROUND(
                    MAX(CASE WHEN c_eau.id_type_flux = 4 THEN c_eau.index_consommation END)
                    -
                    COALESCE(
                        /* Index eau le plus récent AVANT ce jour */
                        (
                            SELECT c_prev.index_consommation FROM consommation c_prev
                            WHERE c_prev.id_hebergement    = %(id)s
                              AND c_prev.id_type_flux      = 4
                              AND c_prev.date_consommation < jours.jour
                            ORDER BY c_prev.date_consommation DESC LIMIT 1
                        ),
                        /* Fallback : index de départ du séjour actif */
                        (
                            SELECT hc.eau_historique_consommation
                            FROM historique_consommation hc
                            JOIN sejour s ON s.id_sejour = hc.id_sejour
                            WHERE s.id_hebergement    = %(id)s
                              AND s.date_debut_sejour <= jours.jour
                              AND s.date_fin_sejour   >= jours.jour
                            ORDER BY hc.id_historique_consommation ASC LIMIT 1
                        )
                    ), 3
                ) AS eau_L,

                /* Consommation électricité du jour = index du jour - index de la veille */
                ROUND(
                    MAX(CASE WHEN c_elec.id_type_flux = 3 THEN c_elec.index_consommation END)
                    -
                    COALESCE(
                        /* Index élec le plus récent AVANT ce jour */
                        (
                            SELECT c_prev.index_consommation FROM consommation c_prev
                            WHERE c_prev.id_hebergement    = %(id)s
                              AND c_prev.id_type_flux      = 3
                              AND c_prev.date_consommation < jours.jour
                            ORDER BY c_prev.date_consommation DESC LIMIT 1
                        ),
                        /* Fallback : index de départ du séjour actif */
                        (
                            SELECT hc.electricite_historique_consommation
                            FROM historique_consommation hc
                            JOIN sejour s ON s.id_sejour = hc.id_sejour
                            WHERE s.id_hebergement    = %(id)s
                              AND s.date_debut_sejour <= jours.jour
                              AND s.date_fin_sejour   >= jours.jour
                            ORDER BY hc.id_historique_consommation ASC LIMIT 1
                        )
                    ), 3
                ) AS electricite_kWh

            FROM (
                /* Génère les 7 derniers jours calendaires (J-6 à aujourd'hui) */
                SELECT CURDATE() - INTERVAL n DAY AS jour
                FROM (
                    SELECT 0 AS n UNION SELECT 1 UNION SELECT 2
                    UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6
                ) seq
            ) jours

            /* Relevés eau du jour exact */
            LEFT JOIN consommation c_eau
                ON c_eau.id_hebergement          = %(id)s
                AND c_eau.id_type_flux           = 4
                AND DATE(c_eau.date_consommation) = jours.jour

            /* Relevés élec du jour exact */
            LEFT JOIN consommation c_elec
                ON c_elec.id_hebergement          = %(id)s
                AND c_elec.id_type_flux           = 3
                AND DATE(c_elec.date_consommation) = jours.jour
        """
        try:
            with closing(MySQLdb.connect(**self.db_config)) as conn:
                with closing(conn.cursor(MySQLdb.cursors.DictCursor)) as cursor:
                    cursor.execute(query, {"id": id_hebergement})
                    rows = cursor.fetchall()
        except Exception as exc:
            log.error("Erreur BDD historique 7j (hebergement %s) : %s", id_hebergement, exc)
            return []

        # Transformation des résultats en liste de dictionnaires
        # avec gestion des valeurs négatives (anomalies)
        return [
            {
                "date":            str(row["date"]),
                # Valeur négative = anomalie (reset compteur) → None
                "eau_L":           float(row["eau_L"])           if row.get("eau_L")           is not None and row["eau_L"]           >= 0 else None,
                "electricite_kWh": float(row["electricite_kWh"]) if row.get("electricite_kWh") is not None and row["electricite_kWh"] >= 0 else None,
            }
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Calcul de différence sécurisé
    # ------------------------------------------------------------------

    @staticmethod
    def _calculer_diff(index_actuel, index_precedent) -> float | None:
        """Retourne index_actuel - index_precedent arrondi à 3 décimales, ou None si invalide."""
        # Calcul sécurisé de la différence entre deux index
        # Retourne None si les valeurs sont manquantes ou si la différence est négative (anomalie)
        if index_actuel is None or index_precedent is None:
            return None
        diff = round(float(index_actuel) - float(index_precedent), 3)
        return diff if diff >= 0 else None  # diff négative = anomalie

    # ------------------------------------------------------------------
    # Publication MQTT
    # ------------------------------------------------------------------

    def publier_tout(self):
        return self.publier_par_consommations(self.get_consommations())

    def publier_par_consommations(self, consommations):
        """Construit et publie le payload MQTT pour chaque hébergement."""
        def build_payload(row):
            # Calcul des différences entre index actuel et précédent
            diff_eau  = self._calculer_diff(row.get("index_eau"),         row.get("index_eau_precedent"))
            diff_elec = self._calculer_diff(row.get("index_electricite"), row.get("index_electricite_precedent"))

            # Récupération de l'historique 7 jours pour cet hébergement
            historique = self.get_historique_7jours(row["id"])

            return {
                "id":  row["id"],
                "nom": row["nom"],
                # Index eau courant et précédent
                "index_eau":           row.get("index_eau"),
                "date_eau":            row.get("date_eau"),
                "index_eau_precedent": row.get("index_eau_precedent"),
                "date_eau_precedent":  row.get("date_eau_precedent"),
                "diff_eau":            diff_eau,
                # Index électricité courant et précédent
                "index_electricite":               row.get("index_electricite"),
                "date_electricite":                row.get("date_electricite"),
                "index_electricite_precedent":     row.get("index_electricite_precedent"),
                "date_electricite_precedent":      row.get("date_electricite_precedent"),
                "diff_electricite":                diff_elec,        # Historique journalier sur 7 jours
                "historique_7j": historique,
            }

        return self.publish_rows(
            consommations,
            payload_builder=build_payload,
            empty_message="Aucun hebergement avec MAC trouve.",
            log_label="consommations",
        )


if __name__ == "__main__":
    pub = ConsommationsPublisher()
    pub.publier_tout()