from contextlib import closing

import MySQLdb

from utils.publisher_base import BasePublisher, log


class DonneesPublisher(BasePublisher):
    """
    Publie vers le broker MQTT les données de consommation de chaque hébergement :
      - Index eau / électricité : dernier + avant-dernier (+ diff)
      - Tableau historique des 7 derniers jours (consommation journalière réelle,
        calculée par rapport à l'index de départ du séjour en cours)
    """

    def __init__(self):
        super().__init__(
            mqtt_client_id="publisher_auto_donnees",
            topic_template="ecocamp/tableau_bord/{mac}/nom_hebergement/{nom}/donnees",
        )

    # ------------------------------------------------------------------
    # Requête principale — index courant + précédent
    # ------------------------------------------------------------------

    def get_donnees(self):
        """
        Récupère pour chaque hébergement avec adresse MAC :
          - Le dernier index eau  (id_type_flux = 4) + l'avant-dernier
          - Le dernier index élec (id_type_flux = 3) + l'avant-dernier
        """
        return self._query_all(
            """
            SELECT
                h.id_hebergement  AS id,
                h.nom_hebergement AS nom,
                h.adresse_mac     AS mac,

                eau_n.index_consommation  AS index_eau,
                eau_n.date_consommation   AS date_eau,
                eau_p.index_consommation  AS index_eau_precedent,
                eau_p.date_consommation   AS date_eau_precedent,

                elec_n.index_consommation AS index_electricite,
                elec_n.date_consommation  AS date_electricite,
                elec_p.index_consommation AS index_electricite_precedent,
                elec_p.date_consommation  AS date_electricite_precedent

            FROM hebergement h

            /* --- Dernier index eau --- */
            LEFT JOIN consommation eau_n
                ON  eau_n.id_hebergement   = h.id_hebergement
                AND eau_n.id_type_flux     = 4
                AND eau_n.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 4
                )

            /* --- Avant-dernier index eau --- */
            LEFT JOIN consommation eau_p
                ON  eau_p.id_hebergement   = h.id_hebergement
                AND eau_p.id_type_flux     = 4
                AND eau_p.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 4
                      AND c.date_consommation < (
                          SELECT MAX(c2.date_consommation) FROM consommation c2
                          WHERE c2.id_hebergement = h.id_hebergement AND c2.id_type_flux = 4
                      )
                )

            /* --- Dernier index électricité --- */
            LEFT JOIN consommation elec_n
                ON  elec_n.id_hebergement   = h.id_hebergement
                AND elec_n.id_type_flux     = 3
                AND elec_n.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 3
                )

            /* --- Avant-dernier index électricité --- */
            LEFT JOIN consommation elec_p
                ON  elec_p.id_hebergement   = h.id_hebergement
                AND elec_p.id_type_flux     = 3
                AND elec_p.date_consommation = (
                    SELECT MAX(c.date_consommation) FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 3
                      AND c.date_consommation < (
                          SELECT MAX(c2.date_consommation) FROM consommation c2
                          WHERE c2.id_hebergement = h.id_hebergement AND c2.id_type_flux = 3
                      )
                )

            WHERE h.adresse_mac IS NOT NULL AND h.adresse_mac != ''
            """
        )

    # ------------------------------------------------------------------
    # Historique 7 jours — consommation journalière réelle
    # ------------------------------------------------------------------

    def get_historique_7jours(self, id_hebergement: int) -> list[dict]:
        """
        Calcule la consommation journalière réelle eau + électricité sur les
        7 derniers jours pour un hébergement.

        Formule par jour J :
            conso_J = MAX(index_J) - dernier_index_avant_J
            avec fallback sur l'index de départ du séjour actif si aucun
            relevé précédent n'existe (premier jour d'un nouveau séjour).

        Retourne une liste de 7 dicts triée par date croissante :
        [
            {
                "date":            "2026-04-03",
                "eau_L":           12.5,    # None si pas de relevé ce jour
                "electricite_kWh": 3.2      # None si pas de relevé ce jour
            },
            ...
        ]
        """
        query = """
            SELECT
                jours.jour AS date,

                /* ---- EAU (id_type_flux = 4) ---- */
                ROUND(
                    MAX(CASE WHEN c_eau.id_type_flux = 4
                        THEN c_eau.index_consommation END)
                    -
                    COALESCE(
                        /* Index eau du relevé le plus récent AVANT ce jour */
                        (
                            SELECT c_prev.index_consommation
                            FROM consommation c_prev
                            WHERE c_prev.id_hebergement   = %(id)s
                              AND c_prev.id_type_flux     = 4
                              AND c_prev.date_consommation < jours.jour
                            ORDER BY c_prev.date_consommation DESC
                            LIMIT 1
                        ),
                        /* Fallback : index de départ du séjour actif ce jour-là */
                        (
                            SELECT hc.eau_historique_consommation
                            FROM historique_consommation hc
                            JOIN sejour s ON s.id_sejour = hc.id_sejour
                            WHERE s.id_hebergement    = %(id)s
                              AND s.date_debut_sejour <= jours.jour
                              AND s.date_fin_sejour   >= jours.jour
                            ORDER BY hc.id_historique_consommation ASC
                            LIMIT 1
                        )
                    ),
                    3
                ) AS eau_L,

                /* ---- ÉLECTRICITÉ (id_type_flux = 3) ---- */
                ROUND(
                    MAX(CASE WHEN c_elec.id_type_flux = 3
                        THEN c_elec.index_consommation END)
                    -
                    COALESCE(
                        (
                            SELECT c_prev.index_consommation
                            FROM consommation c_prev
                            WHERE c_prev.id_hebergement   = %(id)s
                              AND c_prev.id_type_flux     = 3
                              AND c_prev.date_consommation < jours.jour
                            ORDER BY c_prev.date_consommation DESC
                            LIMIT 1
                        ),
                        (
                            SELECT hc.electricite_historique_consommation
                            FROM historique_consommation hc
                            JOIN sejour s ON s.id_sejour = hc.id_sejour
                            WHERE s.id_hebergement    = %(id)s
                              AND s.date_debut_sejour <= jours.jour
                              AND s.date_fin_sejour   >= jours.jour
                            ORDER BY hc.id_historique_consommation ASC
                            LIMIT 1
                        )
                    ),
                    3
                ) AS electricite_kWh

            FROM (
                /* Génère les 7 derniers jours calendaires (J-6 à aujourd'hui) */
                SELECT CURDATE() - INTERVAL n DAY AS jour
                FROM (
                    SELECT 0 AS n UNION SELECT 1 UNION SELECT 2
                    UNION  SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6
                ) seq
            ) jours

            /* Relevés eau du jour exact (LEFT JOIN = jour conservé même sans relevé) */
            LEFT JOIN consommation c_eau
                ON  c_eau.id_hebergement    = %(id)s
                AND c_eau.id_type_flux      = 4
                AND c_eau.date_consommation = jours.jour

            /* Relevés élec du jour exact */
            LEFT JOIN consommation c_elec
                ON  c_elec.id_hebergement    = %(id)s
                AND c_elec.id_type_flux      = 3
                AND c_elec.date_consommation = jours.jour

            GROUP BY jours.jour
            ORDER BY jours.jour ASC
        """

        try:
            with closing(MySQLdb.connect(**self.db_config)) as conn:
                with closing(conn.cursor(MySQLdb.cursors.DictCursor)) as cursor:
                    cursor.execute(query, {"id": id_hebergement})
                    rows = cursor.fetchall()
        except Exception as exc:
            log.error(
                "Erreur BDD historique 7j (hebergement %s) : %s",
                id_hebergement, exc,
            )
            return []

        historique = []
        for row in rows:
            eau  = row.get("eau_L")
            elec = row.get("electricite_kWh")
            historique.append(
                {
                    "date":            str(row["date"]),
                    # Valeur négative = anomalie (ex: reset compteur) → None
                    "eau_L":           float(eau)  if (eau  is not None and eau  >= 0) else None,
                    "electricite_kWh": float(elec) if (elec is not None and elec >= 0) else None,
                }
            )

        return historique

    # ------------------------------------------------------------------
    # Calcul de différence sécurisé
    # ------------------------------------------------------------------

    @staticmethod
    def _calculer_diff(index_actuel, index_precedent) -> float | None:
        """Retourne la différence arrondie à 3 décimales, ou None si données invalides."""
        if index_actuel is None or index_precedent is None:
            return None
        diff = round(float(index_actuel) - float(index_precedent), 3)
        return diff if diff >= 0 else None

    # ------------------------------------------------------------------
    # Publication MQTT
    # ------------------------------------------------------------------

    def publier_tout(self):
        return self.publier_par_donnees(self.get_donnees())

    def publier_par_donnees(self, donnees):
        """
        Construit et publie le payload MQTT pour chaque hébergement.

        Topic : ecocamp/tableau_bord/{mac}/nom_hebergement/{nom}/donnees

        Payload exemple :
        {
            "id": 1, "nom": "Home 1", "mac": "AA:BB:CC:DD:EE:FF",

            "index_eau": 1500.0, "date_eau": "2026-04-09",
            "index_eau_precedent": 1488.0, "date_eau_precedent": "2026-04-08",
            "diff_eau": 12.0,

            "index_electricite": 240.4, "date_electricite": "2026-04-09",
            "index_electricite_precedent": 237.2,
            "date_electricite_precedent": "2026-04-08",
            "diff_electricite": 3.2,

            "historique_7j": [
                {"date": "2026-04-03", "eau_L": 10.5,  "electricite_kWh": 2.8},
                {"date": "2026-04-04", "eau_L": 12.0,  "electricite_kWh": 3.1},
                {"date": "2026-04-05", "eau_L": null,   "electricite_kWh": null},
                {"date": "2026-04-06", "eau_L": 9.3,   "electricite_kWh": 2.5},
                {"date": "2026-04-07", "eau_L": 11.0,  "electricite_kWh": 3.0},
                {"date": "2026-04-08", "eau_L": 13.5,  "electricite_kWh": 3.4},
                {"date": "2026-04-09", "eau_L": 12.0,  "electricite_kWh": 3.2}
            ]
        }
        """
        def build_payload(row):
            diff_eau  = self._calculer_diff(row.get("index_eau"), row.get("index_eau_precedent"))
            diff_elec = self._calculer_diff(
                row.get("index_electricite"),
                row.get("index_electricite_precedent"),
            )
            historique = self.get_historique_7jours(row["id"])

            return {
                "id":  row["id"],
                "nom": row["nom"],
                "mac": row["mac"],

                # --- Index eau ---
                "index_eau":           row.get("index_eau"),
                "date_eau":            row.get("date_eau"),
                "index_eau_precedent": row.get("index_eau_precedent"),
                "date_eau_precedent":  row.get("date_eau_precedent"),
                "diff_eau":            diff_eau,

                # --- Index électricité ---
                "index_electricite":               row.get("index_electricite"),
                "date_electricite":                row.get("date_electricite"),
                "index_electricite_precedent":     row.get("index_electricite_precedent"),
                "date_electricite_precedent":      row.get("date_electricite_precedent"),
                "diff_electricite":                diff_elec,

                # --- Historique 7 jours ---
                "historique_7j": historique,
            }

        return self.publish_rows(
            donnees,
            payload_builder=build_payload,
            empty_message="Aucun hebergement avec MAC trouve.",
            log_label="donnees",
        )


if __name__ == "__main__":
    pub = DonneesPublisher()
    pub.publier_tout()