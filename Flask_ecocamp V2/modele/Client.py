import logging
from datetime import datetime
from utils.hashsel import HashSel 

logger = logging.getLogger(__name__)

class Client:
    def __init__(self, mysql):
        self.mysql = mysql

    # ==========================================
    # --- SECTION AUTHENTIFICATION ---
    # ==========================================

    def test_login(self, login, mdp_saisi):

        cursor = self.mysql.connection.cursor()
        # On récupère le hash stocké pour cet utilisateur
        cursor.execute("SELECT mdp_administrateur FROM administrateur WHERE login_administrateur = %s", (login,))
        res = cursor.fetchone()["mdp_administrateur"]
        cursor.close()

        # --- CORRECTION DE L'INDENTATION ICI ---
        if res:
            reponse = HashSel.tester_hash_sale(mdp_saisi,res)
            if reponse:
                return {"valeur": 1} # Connexion réussie
            return {"valeur": 0} 
        else:
            return {"valeur": 0} 
    

        # ==========================================
    # --- SECTION SEJOURS ---
    # ==========================================

    def get_sejours(self):
        """Récupère tous les séjours avec le nom de l'hébergement, du plus récent au plus ancien."""
        conn = self.mysql.connection
        cursor = conn.cursor()
        requete = """
            SELECT s.id_sejour, s.date_debut_sejour, s.date_fin_sejour, h.nom_hebergement
            FROM sejour s
            JOIN hebergement h ON s.id_hebergement = h.id_hebergement
            ORDER BY s.date_debut_sejour DESC
        """
        cursor.execute(requete)
        res = cursor.fetchall()
        cursor.close()
        return res

    def ajouter_sejour(self, id_h, debut, fin):
        """
        Crée un séjour et initialise son historique de consommation.
        Si aucun relevé n'existe pour ce logement, l'historique est initialisé à 0.
        """
        cursor = self.mysql.connection.cursor()
        try:
            # 1. Insérer le séjour
            cursor.execute(
                "INSERT INTO sejour (date_debut_sejour, date_fin_sejour, id_hebergement) "
                "VALUES (%s, %s, %s)",
                (debut, fin, id_h)
            )
            id_nouveau_sejour = cursor.lastrowid

            # 2. Récupérer les derniers index connus pour ce logement (eau id=4, elec id=3)
            cursor.execute("""
                SELECT id_type_flux, index_consommation
                FROM consommation
                WHERE id_hebergement = %s
                AND id_consommation IN (
                    SELECT MAX(id_consommation)
                    FROM consommation
                    WHERE id_hebergement = %s
                    GROUP BY id_type_flux
                )
            """, (id_h, id_h))
            releves = cursor.fetchall()

            # 3. Construire les valeurs de départ (0 si aucun relevé existant)
            index_eau = 0
            index_elec = 0
            for r in releves:
                type_f = r['id_type_flux'] if isinstance(r, dict) else r[0]
                index_val = r['index_consommation'] if isinstance(r, dict) else r[1]
                if type_f == 4:
                    index_eau = index_val
                elif type_f == 3:
                    index_elec = index_val

            # 4. Insérer la ligne d'historique (toujours, même avec des zéros)
            cursor.execute(
                "INSERT INTO historique_consommation "
                "(id_sejour, eau_historique_consommation, electricite_historique_consommation, date_mesure_historique) "
                "VALUES (%s, %s, %s, %s)",
                (id_nouveau_sejour, index_eau, index_elec, debut)
            )

            self.mysql.connection.commit()
            logger.info("Séjour %s créé pour logement %s (eau_depart=%s, elec_depart=%s)",
                        id_nouveau_sejour, id_h, index_eau, index_elec)
        except Exception as e:
            self.mysql.connection.rollback()
            logger.error("Erreur ajout séjour : %s", e)
            raise e
        finally:
            cursor.close()

    def supprimer_sejour(self, id_sejour):
        """Supprime un séjour et toutes ses dépendances (historique, quotas)."""
        cursor = self.mysql.connection.cursor()
        try:
            cursor.execute("DELETE FROM historique_consommation WHERE id_sejour = %s", (id_sejour,))
            cursor.execute("DELETE FROM quota WHERE id_sejour = %s", (id_sejour,))
            cursor.execute("DELETE FROM sejour WHERE id_sejour = %s", (id_sejour,))
            self.mysql.connection.commit()
            logger.info("Séjour %s supprimé.", id_sejour)
            return True
        except Exception as e:
            self.mysql.connection.rollback()
            logger.error("Erreur suppression séjour %s : %s", id_sejour, e)
            raise e
        finally:
            cursor.close()

    def logement_est_disponible(self, id_h, debut, fin):
        """Retourne True si le logement SPECIFIQUE est libre pour ces dates."""
        cursor = self.mysql.connection.cursor()
        try:
            # La clé est de bien vérifier l'id_hebergement (id_h)
            requete = """
                SELECT COUNT(*) AS total FROM sejour
                WHERE id_hebergement = %s
                AND date_debut_sejour < %s 
                AND date_fin_sejour > %s
            """
            # On passe id_h en premier paramètre
            cursor.execute(requete, (id_h, fin, debut))
            
            resultat = cursor.fetchone()
            # Gestion du format dict ou tuple
            nb_conflits = resultat['total'] if isinstance(resultat, dict) else resultat[0]
            
            return nb_conflits == 0
        except Exception as e:
            logger.error(f"Erreur disponibilité pour logement {id_h} : {e}")
            return False
        finally:
            cursor.close()



    # ==========================================
    # --- SECTION HEBERGEMENTS ET TYPES ---
    # ==========================================

    def get_hebergements(self):
        """Récupère la liste de tous les hébergements (ID et Nom)."""
        conn = self.mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT id_hebergement, nom_hebergement FROM hebergement")
        res = cursor.fetchall()
        cursor.close()
        return res

    def get_types_logement(self):
        """Récupère toutes les catégories de logement avec leurs quotas."""
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "SELECT id_type_logement, nom_type, quota_eau_max, quota_elec_max FROM type_logement"
        )
        res = cursor.fetchall()
        cursor.close()
        return res

    def modifier_quota_type(self, id_type, q_eau, q_elec):
        """Met à jour les quotas de consommation pour une catégorie de logement."""
        conn = self.mysql.connection
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE type_logement SET quota_eau_max = %s, quota_elec_max = %s "
            "WHERE id_type_logement = %s",
            (q_eau, q_elec, id_type)
        )
        conn.commit()
        cursor.close()

    # ==========================================
    # --- SECTION CONSOMMATIONS ---
    # ==========================================

    def get_consommations(self):
        """Récupère les 50 derniers relevés de consommation toutes catégories confondues."""
        conn = self.mysql.connection
        cursor = conn.cursor()
        requete = """
            SELECT
                c.index_consommation,
                c.date_consommation,
                f.nom_type_flux,
                f.id_type_flux,
                t.quota_eau_max,
                t.quota_elec_max,
                t.nom_type
            FROM consommation c
            JOIN type_flux f ON c.id_type_flux = f.id_type_flux
            JOIN hebergement h ON c.id_hebergement = h.id_hebergement
            JOIN type_logement t ON h.id_type_logement = t.id_type_logement
            ORDER BY c.date_consommation DESC LIMIT 50
        """
        cursor.execute(requete)
        res = cursor.fetchall()
        cursor.close()
        return res

    def get_consommations_par_hebergement(self, id_hebergement):
        """Récupère les relevés d'un hébergement précis avec calcul de la conso réelle du séjour."""
        cursor = self.mysql.connection.cursor()
        requete = """
            SELECT
                c.index_consommation,
                c.date_consommation,
                f.nom_type_flux,
                f.id_type_flux,
                (c.index_consommation - histo.eau_historique_consommation) AS conso_reelle_eau,
                (c.index_consommation - histo.electricite_historique_consommation) AS conso_reelle_elec,
                t.quota_eau_max,
                t.quota_elec_max
            FROM consommation c
            JOIN type_flux f ON c.id_type_flux = f.id_type_flux
            JOIN sejour s ON c.id_hebergement = s.id_hebergement
                AND c.date_consommation BETWEEN s.date_debut_sejour AND s.date_fin_sejour
            JOIN historique_consommation histo ON s.id_sejour = histo.id_sejour
            JOIN hebergement heb ON c.id_hebergement = heb.id_hebergement
            JOIN type_logement t ON heb.id_type_logement = t.id_type_logement
            WHERE c.id_hebergement = %s
            ORDER BY c.date_consommation DESC
        """
        cursor.execute(requete, (id_hebergement,))
        res = cursor.fetchall()
        cursor.close()
        return res

    # ==========================================
    # --- SECTION MESSAGES ---
    # ==========================================

    def get_messages(self):
        """Récupère tous les messages avec leur type, triés par date décroissante."""
        cursor = self.mysql.connection.cursor()
        cursor.execute("""
            SELECT m.id_message, m.contenu_message, m.date_debut_message,
                   m.date_fin_message, m.horaire_evenement_message, tm.nom_type_message
            FROM message m
            JOIN type_message tm ON m.id_type_message = tm.id_type_message
            ORDER BY m.date_debut_message DESC
        """)
        res = cursor.fetchall()
        cursor.close()
        return res

    def get_types_message(self):
        """Récupère les types de message disponibles."""
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id_type_message, nom_type_message FROM type_message")
        res = cursor.fetchall()
        cursor.close()
        return res

    def ajouter_message(self, contenu, date_debut, date_fin, horaire, id_type):
        """Insère un nouveau message en base."""
        cursor = self.mysql.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO message (contenu_message, date_debut_message, date_fin_message, "
                "horaire_evenement_message, id_type_message) VALUES (%s, %s, %s, %s, %s)",
                (contenu, date_debut, date_fin, horaire or None, id_type)
            )
            self.mysql.connection.commit()
            logger.info("Message ajouté (type %s)", id_type)
        except Exception as e:
            self.mysql.connection.rollback()
            logger.error("Erreur ajout message : %s", e)
            raise e
        finally:
            cursor.close()

    def supprimer_message(self, id_message):
        """Supprime un message par son ID."""
        cursor = self.mysql.connection.cursor()
        try:
            cursor.execute("DELETE FROM message WHERE id_message = %s", (id_message,))
            self.mysql.connection.commit()
            logger.info("Message %s supprimé.", id_message)
        except Exception as e:
            self.mysql.connection.rollback()
            logger.error("Erreur suppression message %s : %s", id_message, e)
            raise e
        finally:
            cursor.close()