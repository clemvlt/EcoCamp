from datetime import datetime

class Client:
    def __init__(self, mysql):
        self.mysql = mysql

    # --- SECTION AUTHENTICATION ---
    def test_login(self, login, mdp):
        conn = self.mysql.connection
        cursor = conn.cursor()
        requete = "SELECT count(*) as valeur FROM administrateur WHERE login_administrateur = %s AND mdp_administrateur = %s"
        cursor.execute(requete, (login, mdp))
        res = cursor.fetchone()
        cursor.close()
        return res   

    # --- SECTION SEJOURS ---
    def get_sejours(self):
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
        conn = self.mysql.connection
        cursor = conn.cursor()
        requete = "INSERT INTO sejour (date_debut_sejour, date_fin_sejour, id_hebergement) VALUES (%s, %s, %s)"
        cursor.execute(requete, (debut, fin, id_h))
        conn.commit()
        cursor.close()

    def supprimer_sejour(self, id_sejour):
        conn = self.mysql.connection
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sejour WHERE id_sejour = %s", (id_sejour,))
        conn.commit()
        cursor.close()

    # --- SECTION HEBERGEMENTS ET TYPES ---
    def get_hebergements(self):
        conn = self.mysql.connection
        cursor = conn.cursor()
        requete = "SELECT id_hebergement, nom_hebergement FROM hebergement"
        cursor.execute(requete)
        res = cursor.fetchall()
        cursor.close()
        return res

    def get_types_logement(self):
        conn = self.mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM type_logement")
        res = cursor.fetchall()
        cursor.close()
        return res

    def modifier_quota_type(self, id_type, q_eau, q_elec):
        conn = self.mysql.connection
        cursor = conn.cursor()
        requete = "UPDATE type_logement SET quota_eau_max = %s, quota_elec_max = %s WHERE id_type_logement = %s"
        cursor.execute(requete, (q_eau, q_elec, id_type))
        conn.commit()
        cursor.close()

    # --- SECTION CONSOMMATIONS (CORRIGÉE POUR LE TEMPLATE) ---
    def get_consommations(self):
            conn = self.mysql.connection
            cursor = conn.cursor()
            # On récupère l'index de consommation ET le quota du type de logement
            requete = """
                SELECT 
                    c.index_consommation, 
                    c.date_consommation, 
                    f.nom_type_flux, 
                    t.quota_eau_max, 
                    t.quota_elec_max, 
                    t.nom_type,
                    f.id_type_flux
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
        conn = self.mysql.connection
        cursor = conn.cursor()
        requete = """
            SELECT 
                c.index_consommation, 
                c.date_consommation, 
                f.nom_type_flux,
                t.quota_eau_max, 
                t.quota_elec_max,
                # Sous-requête : on cherche l'index le plus ancien DEPUIS le début du séjour
                (SELECT MIN(c2.index_consommation) 
                FROM consommation c2 
                WHERE c2.id_hebergement = c.id_hebergement 
                AND c2.id_type_flux = c.id_type_flux
                AND c2.date_consommation >= s.date_debut_sejour) as index_depart,
                f.id_type_flux
            FROM consommation c
            JOIN type_flux f ON c.id_type_flux = f.id_type_flux
            JOIN hebergement h ON c.id_hebergement = h.id_hebergement
            JOIN type_logement t ON h.id_type_logement = t.id_type_logement
            JOIN sejour s ON h.id_hebergement = s.id_hebergement
            WHERE c.id_hebergement = %s
            AND c.date_consommation >= s.date_debut_sejour
            AND s.date_fin_sejour >= NOW()
            ORDER BY c.date_consommation DESC
        """
        cursor.execute(requete, (id_hebergement,))
        res = cursor.fetchall()
        cursor.close()
        return res
        

    def ajouter_sejour(self, id_h, debut, fin):
        conn = self.mysql.connection
        cursor = conn.cursor()

        try:
            # 1. Récupérer l'index actuel du compteur d'ÉLECTRICITÉ (Type 3) pour cet hébergement
            cursor.execute("""
                SELECT index_compteur FROM compteur 
                WHERE id_hebergement = %s AND id_type_flux = 3
            """, (id_h,))
            res_elec = cursor.fetchone()
            valeur_depart_elec = res_elec[0] if res_elec else 0

            # 2. Récupérer l'index actuel du compteur d'EAU (Type 4) pour cet hébergement
            cursor.execute("""
                SELECT index_compteur FROM compteur 
                WHERE id_hebergement = %s AND id_type_flux = 4
            """, (id_h,))
            res_eau = cursor.fetchone()
            valeur_depart_eau = res_eau[0] if res_eau else 0

            # 3. Créer le séjour avec ces index de référence
            # (Assurez-vous d'avoir ajouté les colonnes index_depart_eau/elec à la table sejour)
            requete = """
                INSERT INTO sejour (date_debut_sejour, date_fin_sejour, id_hebergement, 
                                index_depart_eau, index_depart_elec) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(requete, (debut, fin, id_h, valeur_depart_eau, valeur_depart_elec))
            
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'ajout du séjour : {e}")
            conn.rollback()
        finally:
            cursor.close()

    def get_types_logement(self):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id_type_logement, nom_type, quota_eau_max, quota_elec_max FROM type_logement")
        res = cursor.fetchall()
        cursor.close()
        return res


