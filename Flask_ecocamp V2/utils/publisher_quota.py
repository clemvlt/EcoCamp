from utils.publisher_base import BasePublisher


class QuotaPublisher(BasePublisher):
    def __init__(self):
        super().__init__(
            mqtt_client_id="publisher_auto_quota",
            topic_template="ecocamp/tableau_bord/{mac}/nom_hebergement/{nom}/quota",
        )

    def get_quotas(self):
        """
        Publie toujours un topic quota pour chaque hebergement avec MAC.
        Node-RED peut ainsi afficher un etat stable, meme sans sejour en cours.
        """
        return self._query_all(
            """
            SELECT
                h.id_hebergement AS id,
                h.nom_hebergement AS nom,
                h.adresse_mac AS mac,
                tl.nom_type AS type_logement,
                s.id_sejour AS id_sejour,
                s.date_debut_sejour AS date_debut,
                s.date_fin_sejour AS date_fin,
                q.eau_quota AS quota_eau_sejour,
                q.electicite_quota AS quota_electricite_sejour,
                tl.quota_eau_max AS quota_eau_max,
                tl.quota_elec_max AS quota_elec_max,
                eau.index_consommation AS conso_eau,
                eau.date_consommation AS date_conso_eau,
                elec.index_consommation AS conso_electricite,
                elec.date_consommation AS date_conso_electricite
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
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 4
                )
            LEFT JOIN consommation elec
                ON elec.id_hebergement = h.id_hebergement
                AND elec.id_type_flux = 3
                AND elec.date_consommation = (
                    SELECT MAX(c.date_consommation)
                    FROM consommation c
                    WHERE c.id_hebergement = h.id_hebergement AND c.id_type_flux = 3
                )
            WHERE h.adresse_mac IS NOT NULL AND h.adresse_mac != ''
            """
        )

    @staticmethod
    def _pct(conso, quota):
        if conso is not None and quota and quota > 0:
            return round(conso / quota * 100, 2)
        return None

    def publier_tout(self):
        return self.publier_par_quota(self.get_quotas())

    def publier_par_quota(self, quotas):
        def build_payload(row):
            quota_eau = row.get("quota_eau_sejour") or row.get("quota_eau_max")
            quota_elec = row.get("quota_electricite_sejour") or row.get("quota_elec_max")
            return {
                "id": row["id"],
                "nom": row["nom"],
                "mac": row["mac"],
                "type_logement": row.get("type_logement"),
                "sejour_actif": row.get("id_sejour") is not None,
                "id_sejour": row.get("id_sejour"),
                "date_debut": row.get("date_debut"),
                "date_fin": row.get("date_fin"),
                "quota_eau": quota_eau,
                "quota_eau_sejour": row.get("quota_eau_sejour"),
                "quota_eau_max": row.get("quota_eau_max"),
                "conso_eau": row.get("conso_eau"),
                "date_conso_eau": row.get("date_conso_eau"),
                "pct_eau": self._pct(row.get("conso_eau"), quota_eau),
                "quota_electricite": quota_elec,
                "quota_electricite_sejour": row.get("quota_electricite_sejour"),
                "quota_elec_max": row.get("quota_elec_max"),
                "conso_electricite": row.get("conso_electricite"),
                "date_conso_electricite": row.get("date_conso_electricite"),
                "pct_electricite": self._pct(row.get("conso_electricite"), quota_elec),
            }

        return self.publish_rows(
            quotas,
            payload_builder=build_payload,
            empty_message="Aucun hebergement avec MAC trouve.",
            log_label="quota",
        )


if __name__ == "__main__":
    pub = QuotaPublisher()
    pub.publier_tout()
