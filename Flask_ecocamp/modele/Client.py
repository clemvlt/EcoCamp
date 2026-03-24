from datetime import datetime

class Client:
    """
    Classe gérant les interactions avec la base de données MariaDB/MySQL.
    Centralise toutes les requêtes SQL liées aux administrateurs, séjours et consommations.
    """
    def __init__(self, mysql):
        # Initialisation de la connexion MySQL fournie par l'application Flask
        self.mysql = mysql

    # ==========================================
    # --- SECTION AUTHENTIFICATION ---
    # ==========================================

    def test_login(self, login, mdp):
        """
        Vérifie si les identifiants correspondent à un compte administrateur.
        Retourne un dictionnaire (grâce au cursor) contenant le nombre de correspondances (0 ou 1).
        """
        conn = self.mysql.connection
        cursor = conn.cursor()
        requete = "SELECT count(*) as valeur FROM administrateur WHERE login_administrateur = %s AND mdp_administrateur = %s"
        cursor.execute(requete, (login, mdp))
        res = cursor.fetchone()
        cursor.close()
        return res   

    # ==========================================
    # --- SECTION SEJOURS ---
    # ==========================================

    def get_sejours(self):
        """
        Récupère la liste de tous les séjours avec le nom de l'hébergement associé.
        Triés du plus récent au plus ancien.
        """
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

    def supprimer_sejour(self, id_sejour):
        cursor = self.mysql.connection.cursor()
        try:
            # 1. Supprimer les consommations liées à ce séjour
            cursor.execute("DELETE FROM historique_cosommation WHERE id_sejour = %s", (id_sejour,))
            
            # 2. Supprimer les quotas liés à ce séjour (C'est l'erreur que tu as maintenant)
            cursor.execute("DELETE FROM quota WHERE id_sejour = %s", (id_sejour,))
            
            # 3. S'il y a d'autres tables (ex: alertes ou messages liés au séjour), ajoute-les ici
            # cursor.execute("DELETE FROM alertes WHERE id_sejour = %s", (id_sejour,))

            # 4. Enfin, supprimer le séjour lui-même
            cursor.execute("DELETE FROM sejour WHERE id_sejour = %s", (id_sejour,))
            
            # On valide toutes les suppressions d'un coup
            self.mysql.connection.commit()
            return True
        except Exception as e:
            # En cas de problème, on annule tout pour ne pas avoir de données incohérentes
            self.mysql.connection.rollback()
            print(f"Erreur lors de la suppression du séjour {id_sejour} : {e}")
            raise e
        finally:
            cursor.close()

    def ajouter_sejour(self, id_h, debut, fin):
        cursor = self.mysql.connection.cursor()
        try:
            # Requête d'insertion
            cursor.execute("""
                INSERT INTO sejour (id_hebergement, date_debut_sejour, date_fin_sejour)
                VALUES (%s, %s, %s)
            """, (id_h, debut, fin))
            
            # IMPORTANT : Toujours valider la transaction pour Flask-MySQL
            self.mysql.connection.commit()
        except Exception as e:
            print(f"Erreur lors de la création du séjour : {e}")
            self.mysql.connection.rollback() # Annule en cas d'erreur
        finally:
            cursor.close()

    # ==========================================
    # --- SECTION HEBERGEMENTS ET TYPES ---
    # ==========================================

    def get_hebergements(self):
        """Récupère la liste simple de tous les hébergements (ID et Nom)."""
        conn = self.mysql.connection
        cursor = conn.cursor()
        requete = "SELECT id_hebergement, nom_hebergement FROM hebergement"
        cursor.execute(requete)
        res = cursor.fetchall()
        cursor.close()
        return res

    def get_types_logement(self):
        """
        Récupère toutes les catégories de logement (Standard, Luxe, etc.)
        et leurs quotas associés.
        """
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id_type_logement, nom_type, quota_eau_max, quota_elec_max FROM type_logement")
        res = cursor.fetchall()
        cursor.close()
        return res

    def modifier_quota_type(self, id_type, q_eau, q_elec):
        """
        Met à jour les limites (quotas) de consommation pour une catégorie spécifique.
        """
        conn = self.mysql.connection
        cursor = conn.cursor()
        requete = "UPDATE type_logement SET quota_eau_max = %s, quota_elec_max = %s WHERE id_type_logement = %s"
        cursor.execute(requete, (q_eau, q_elec, id_type))
        conn.commit()
        cursor.close()

    # ==========================================
    # --- SECTION CONSOMMATIONS ---
    # ==========================================

    def get_consommations(self):
        """
        Récupère les 50 derniers relevés de consommation toutes catégories confondues.
        Inclut les quotas pour permettre l'affichage des alertes dans le template.
        """
        conn = self.mysql.connection
        cursor = conn.cursor()
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
        # On enlève la condition temporelle stricte pour le test
        requete = """
            SELECT 
                c.index_consommation, 
                c.date_consommation, 
                f.nom_type_flux,
                t.quota_eau_max, 
                t.quota_elec_max,
                # On prend l'index le plus bas trouvé pour cet hébergement comme départ
                (SELECT MIN(c2.index_consommation) 
                FROM consommation c2 
                WHERE c2.id_hebergement = c.id_hebergement 
                AND c2.id_type_flux = c.id_type_flux) as index_depart,
                f.id_type_flux
            FROM consommation c
            JOIN type_flux f ON c.id_type_flux = f.id_type_flux
            JOIN hebergement h ON c.id_hebergement = h.id_hebergement
            JOIN type_logement t ON h.id_type_logement = t.id_type_logement
            WHERE c.id_hebergement = %s
            ORDER BY c.date_consommation DESC
        """
        cursor.execute(requete, (id_hebergement,))
        res = cursor.fetchall()
        cursor.close()
        return res