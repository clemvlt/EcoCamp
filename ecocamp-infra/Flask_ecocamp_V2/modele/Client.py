from utils.hashsel import HashSel
from datetime import datetime, timedelta


class Client:
    def __init__(self, mysql):
        self.mysql = mysql


    # ==========================================
    # --- AUTHENTIFICATION ---
    # ==========================================

    def test_login(self, login, mdp_saisi):
        """Vérifie si le login et le mot de passe sont corrects."""
        cursor = self.mysql.connection.cursor()

        cursor.execute(
            "SELECT mdp_administrateur FROM administrateur WHERE login_administrateur = %s",
            (login,)
        )
        res = cursor.fetchone()
        cursor.close()

        if res and HashSel.tester_hash_sale(mdp_saisi, res["mdp_administrateur"]):
            return {"valeur": 1}
        return {"valeur": 0}


    # ==========================================
    # --- SÉJOURS ---
    # ==========================================

    def get_sejours(self):
        """Retourne tous les séjours avec le nom du logement, du plus récent au plus ancien."""
        cursor = self.mysql.connection.cursor()

        cursor.execute("""
            SELECT s.id_sejour,
                   s.date_debut_sejour,
                   s.date_fin_sejour,
                   h.nom_hebergement
            FROM sejour s
            JOIN hebergement h ON s.id_hebergement = h.id_hebergement
            ORDER BY s.date_debut_sejour DESC
        """)

        res = cursor.fetchall()
        cursor.close()
        return res

    def logement_est_disponible(self, id_h, debut, fin):
        """Retourne True si le logement est libre sur la période demandée."""
        cursor = self.mysql.connection.cursor()

        cursor.execute("""
            SELECT COUNT(*) AS nb_conflits
            FROM sejour
            WHERE id_hebergement    = %s
              AND date_debut_sejour  < %s
              AND date_fin_sejour    > %s
        """, (id_h, fin, debut))

        res = cursor.fetchone()
        cursor.close()

        nb_conflits = res["nb_conflits"] if isinstance(res, dict) else res[0]
        return nb_conflits == 0

    def ajouter_sejour(self, id_h, debut, fin):
        """Crée un séjour et enregistre les index de départ (eau + électricité)."""
        cursor = self.mysql.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO sejour (date_debut_sejour, date_fin_sejour, id_hebergement) VALUES (%s, %s, %s)",
                (debut, fin, id_h)
            )
            id_sejour = cursor.lastrowid

            cursor.execute("""
                SELECT index_consommation FROM consommation
                WHERE id_hebergement = %s AND id_type_flux = 4
                ORDER BY id_consommation DESC LIMIT 1
            """, (id_h,))
            row = cursor.fetchone()
            index_eau = row["index_consommation"] if row else 0

            cursor.execute("""
                SELECT index_consommation FROM consommation
                WHERE id_hebergement = %s AND id_type_flux = 3
                ORDER BY id_consommation DESC LIMIT 1
            """, (id_h,))
            row = cursor.fetchone()
            index_elec = row["index_consommation"] if row else 0

            cursor.execute("""
                INSERT INTO historique_consommation
                    (id_sejour, eau_historique_consommation, electricite_historique_consommation, date_mesure_historique)
                VALUES (%s, %s, %s, %s)
            """, (id_sejour, index_eau, index_elec, debut))

            self.mysql.connection.commit()

        except Exception as e:
            self.mysql.connection.rollback()
            raise e
        finally:
            cursor.close()

    def supprimer_sejour(self, id_sejour):
        """Supprime un séjour ainsi que son historique et ses quotas associés."""
        cursor = self.mysql.connection.cursor()
        try:
            cursor.execute("DELETE FROM historique_consommation WHERE id_sejour = %s", (id_sejour,))
            cursor.execute("DELETE FROM quota WHERE id_sejour = %s", (id_sejour,))
            cursor.execute("DELETE FROM sejour WHERE id_sejour = %s", (id_sejour,))
            self.mysql.connection.commit()
            return True
        except Exception as e:
            self.mysql.connection.rollback()
            raise e
        finally:
            cursor.close()


    # ==========================================
    # --- HÉBERGEMENTS ET TYPES ---
    # ==========================================

    def get_hebergements(self):
        """Retourne la liste de tous les logements (ID + nom)."""
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id_hebergement, nom_hebergement FROM hebergement")
        res = cursor.fetchall()
        cursor.close()
        return res

    def get_types_logement(self):
        """Retourne toutes les catégories de logement avec leurs quotas max."""
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "SELECT id_type_logement, nom_type, quota_eau_max, quota_elec_max FROM type_logement"
        )
        res = cursor.fetchall()
        cursor.close()
        return res

    def modifier_quota_type(self, id_type, q_eau, q_elec):
        """Met à jour les quotas d'eau et d'électricité d'une catégorie de logement."""
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "UPDATE type_logement SET quota_eau_max = %s, quota_elec_max = %s WHERE id_type_logement = %s",
            (q_eau, q_elec, id_type)
        )
        self.mysql.connection.commit()
        cursor.close()


    # ==========================================
    # --- CONSOMMATIONS ---
    # ==========================================

    def get_consommations(self):
        """
        Retourne les relevés de TOUS les logements sur les 7 derniers jours,
        avec la consommation réelle calculée depuis le début du séjour.
        """
        cursor = self.mysql.connection.cursor()
        date_limite = datetime.now() - timedelta(days=7)

        cursor.execute("""
            SELECT c.index_consommation,
                   c.date_consommation,
                   f.nom_type_flux,
                   f.id_type_flux,
                   h.nom_hebergement,
                   CASE
                       WHEN f.id_type_flux = 4 THEN (c.index_consommation - histo.eau_historique_consommation)
                       ELSE NULL
                   END AS conso_reelle_eau,
                   CASE
                       WHEN f.id_type_flux = 3 THEN (c.index_consommation - histo.electricite_historique_consommation)
                       ELSE NULL
                   END AS conso_reelle_elec,
                   t.quota_eau_max,
                   t.quota_elec_max
            FROM consommation c
            JOIN type_flux f ON c.id_type_flux = f.id_type_flux
            JOIN sejour s ON c.id_hebergement = s.id_hebergement
                AND c.date_consommation BETWEEN s.date_debut_sejour AND s.date_fin_sejour
            JOIN historique_consommation histo ON s.id_sejour = histo.id_sejour
            JOIN hebergement h ON c.id_hebergement = h.id_hebergement
            JOIN type_logement t ON h.id_type_logement = t.id_type_logement
            WHERE c.date_consommation >= %s
            ORDER BY c.date_consommation DESC
        """, (date_limite,))

        res = cursor.fetchall()
        cursor.close()
        return res

    def get_consommations_par_hebergement(self, id_hebergement):
        """
        Retourne les relevés d'un logement sur les 7 derniers jours
        avec la consommation réelle calculée depuis le début du séjour.
        """
        cursor = self.mysql.connection.cursor()
        date_limite = datetime.now() - timedelta(days=7)

        cursor.execute("""
            SELECT c.index_consommation,
                   c.date_consommation,
                   f.nom_type_flux,
                   f.id_type_flux,
                   h.nom_hebergement,
                   CASE
                       WHEN f.id_type_flux = 4 THEN (c.index_consommation - histo.eau_historique_consommation)
                       ELSE NULL
                   END AS conso_reelle_eau,
                   CASE
                       WHEN f.id_type_flux = 3 THEN (c.index_consommation - histo.electricite_historique_consommation)
                       ELSE NULL
                   END AS conso_reelle_elec,
                   t.quota_eau_max,
                   t.quota_elec_max
            FROM consommation c
            JOIN type_flux f ON c.id_type_flux = f.id_type_flux
            JOIN sejour s ON c.id_hebergement = s.id_hebergement
                AND c.date_consommation BETWEEN s.date_debut_sejour AND s.date_fin_sejour
            JOIN historique_consommation histo ON s.id_sejour = histo.id_sejour
            JOIN hebergement h ON c.id_hebergement = h.id_hebergement
            JOIN type_logement t ON h.id_type_logement = t.id_type_logement
            WHERE c.id_hebergement = %s
              AND c.date_consommation >= %s
            ORDER BY c.date_consommation DESC
        """, (id_hebergement, date_limite))

        res = cursor.fetchall()
        cursor.close()
        return res


    # ==========================================
    # --- MESSAGES ---
    # ==========================================

    def get_messages(self):
        """Retourne tous les messages avec leur type, du plus récent au plus ancien."""
        cursor = self.mysql.connection.cursor()

        cursor.execute("""
            SELECT m.id_message,
                   m.contenu_message,
                   m.date_debut_message,
                   m.date_fin_message,
                   m.horaire_evenement_message,
                   tm.nom_type_message
            FROM message m
            JOIN type_message tm ON m.id_type_message = tm.id_type_message
            ORDER BY m.date_debut_message DESC
        """)

        res = cursor.fetchall()
        cursor.close()
        return res

    def get_types_message(self):
        """Retourne les types de message disponibles."""
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id_type_message, nom_type_message FROM type_message")
        res = cursor.fetchall()
        cursor.close()
        return res

    def ajouter_message(self, contenu, date_debut, date_fin, horaire, id_type):
        """Insère un nouveau message en base."""
        cursor = self.mysql.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO message
                    (contenu_message, date_debut_message, date_fin_message,
                     horaire_evenement_message, id_type_message)
                VALUES (%s, %s, %s, %s, %s)
            """, (contenu, date_debut, date_fin, horaire or None, id_type))
            self.mysql.connection.commit()
        except Exception as e:
            self.mysql.connection.rollback()
            raise e
        finally:
            cursor.close()

    def supprimer_message(self, id_message):
        """Supprime un message par son ID."""
        cursor = self.mysql.connection.cursor()
        try:
            cursor.execute("DELETE FROM message WHERE id_message = %s", (id_message,))
            self.mysql.connection.commit()
        except Exception as e:
            self.mysql.connection.rollback()
            raise e
        finally:
            cursor.close()