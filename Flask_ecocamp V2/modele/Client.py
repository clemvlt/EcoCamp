from utils.hashsel import HashSel
from datetime import datetime, timedelta
import json


class Client:
    def __init__(self, mysql, mqtt_client=None):
        self.mysql = mysql
        self.mqtt_client = mqtt_client


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
            WHERE id_hebergement   = %s
              AND date_debut_sejour < %s
              AND date_fin_sejour   > %s
        """, (id_h, fin, debut))
        res = cursor.fetchone()
        cursor.close()
        nb_conflits = res["nb_conflits"] if isinstance(res, dict) else res[0]
        return nb_conflits == 0

    def ajouter_sejour(self, id_h, debut, fin):
        """
        Crée un séjour et enregistre les index de départ réels (eau + électricité)
        dans historique_consommation.

        CORRECTION : on récupère le dernier index par date_consommation DESC
        (et non par id DESC) pour garantir la valeur la plus récente.
        Si aucune consommation n'existe encore pour ce logement, l'index de
        départ est mis à 0 — cela sera correct dès que le compteur enverra
        sa première valeur.
        """
        cursor = self.mysql.connection.cursor()
        try:
            # 1. Création du séjour
            cursor.execute(
                "INSERT INTO sejour (date_debut_sejour, date_fin_sejour, id_hebergement) "
                "VALUES (%s, %s, %s)",
                (debut, fin, id_h)
            )
            id_sejour = cursor.lastrowid

            # 2. Index de départ EAU (id_type_flux = 4)
            #    On prend la mesure dont la date est <= début du séjour,
            #    la plus proche dans le passé.
            cursor.execute("""
                SELECT index_consommation
                FROM consommation
                WHERE id_hebergement = %s
                  AND id_type_flux   = 4
                  AND date_consommation <= %s
                ORDER BY date_consommation DESC
                LIMIT 1
            """, (id_h, debut))
            row = cursor.fetchone()
            index_eau = (row["index_consommation"] if isinstance(row, dict) else row[0]) if row else 0

            # 3. Index de départ ÉLECTRICITÉ (id_type_flux = 3)
            cursor.execute("""
                SELECT index_consommation
                FROM consommation
                WHERE id_hebergement = %s
                  AND id_type_flux   = 3
                  AND date_consommation <= %s
                ORDER BY date_consommation DESC
                LIMIT 1
            """, (id_h, debut))
            row = cursor.fetchone()
            index_elec = (row["index_consommation"] if isinstance(row, dict) else row[0]) if row else 0

            # 4. Enregistrement de la ligne de départ dans historique_consommation
            #    C'est cette valeur qui servira de référence pour calculer
            #    la consommation réelle : conso = index_actuel - index_depart
            cursor.execute("""
                INSERT INTO historique_consommation
                    (id_sejour,
                     eau_historique_consommation,
                     electricite_historique_consommation,
                     date_mesure_historique)
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

    def get_hebergements_avec_mac(self):
        """
        Retourne tous les logements avec leur adresse MAC et leur type.
        Utilisé par le publisher MQTT pour diffuser la liste des tableaux de bord.
        """
        cursor = self.mysql.connection.cursor()
        cursor.execute("""
            SELECT h.id_hebergement,
                   h.nom_hebergement,
                   h.adresse_mac,
                   t.nom_type,
                   t.quota_eau_max,
                   t.quota_elec_max
            FROM hebergement h
            JOIN type_logement t ON h.id_type_logement = t.id_type_logement
            ORDER BY h.id_hebergement
        """)
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
        Retourne les relevés de TOUS les logements sur les 7 derniers jours.

        conso_reelle = index_actuel - index_départ_séjour
        Si le relevé est hors séjour actif, conso_reelle vaut NULL.
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
                       WHEN f.id_type_flux = 4 AND histo.eau_historique_consommation IS NOT NULL
                       THEN (c.index_consommation - histo.eau_historique_consommation)
                       ELSE NULL
                   END AS conso_reelle_eau,
                   CASE
                       WHEN f.id_type_flux = 3 AND histo.electricite_historique_consommation IS NOT NULL
                       THEN (c.index_consommation - histo.electricite_historique_consommation)
                       ELSE NULL
                   END AS conso_reelle_elec,
                   t.quota_eau_max,
                   t.quota_elec_max
            FROM consommation c
            JOIN type_flux     f ON c.id_type_flux    = f.id_type_flux
            JOIN hebergement   h ON c.id_hebergement  = h.id_hebergement
            JOIN type_logement t ON h.id_type_logement = t.id_type_logement
            LEFT JOIN sejour   s ON c.id_hebergement  = s.id_hebergement
                AND c.date_consommation BETWEEN s.date_debut_sejour AND s.date_fin_sejour
            LEFT JOIN (
                SELECT id_sejour,
                       eau_historique_consommation,
                       electricite_historique_consommation
                FROM historique_consommation h1
                WHERE id_historique_consommation = (
                    SELECT MIN(id_historique_consommation)
                    FROM historique_consommation h2
                    WHERE h2.id_sejour = h1.id_sejour
                )
            ) histo ON s.id_sejour = histo.id_sejour
            WHERE c.date_consommation >= %s
            ORDER BY c.date_consommation DESC
        """, (date_limite,))

        res = cursor.fetchall()
        cursor.close()
        return res

    def get_consommations_par_hebergement(self, id_hebergement):
        """
        Retourne les relevés d'un logement sur les 7 derniers jours.

        conso_reelle = index_actuel - index_départ_séjour
        Si le relevé est hors séjour actif, conso_reelle vaut NULL.
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
                       WHEN f.id_type_flux = 4 AND histo.eau_historique_consommation IS NOT NULL
                       THEN (c.index_consommation - histo.eau_historique_consommation)
                       ELSE NULL
                   END AS conso_reelle_eau,
                   CASE
                       WHEN f.id_type_flux = 3 AND histo.electricite_historique_consommation IS NOT NULL
                       THEN (c.index_consommation - histo.electricite_historique_consommation)
                       ELSE NULL
                   END AS conso_reelle_elec,
                   t.quota_eau_max,
                   t.quota_elec_max
            FROM consommation c
            JOIN type_flux     f ON c.id_type_flux    = f.id_type_flux
            JOIN hebergement   h ON c.id_hebergement  = h.id_hebergement
            JOIN type_logement t ON h.id_type_logement = t.id_type_logement
            LEFT JOIN sejour   s ON c.id_hebergement  = s.id_hebergement
                AND c.date_consommation BETWEEN s.date_debut_sejour AND s.date_fin_sejour
            LEFT JOIN (
                SELECT id_sejour,
                       eau_historique_consommation,
                       electricite_historique_consommation
                FROM historique_consommation h1
                WHERE id_historique_consommation = (
                    SELECT MIN(id_historique_consommation)
                    FROM historique_consommation h2
                    WHERE h2.id_sejour = h1.id_sejour
                )
            ) histo ON s.id_sejour = histo.id_sejour
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


    # ==========================================
    # --- MQTT ---
    # ==========================================

    def envoyer_conso_mqtt(self, id_h, id_flux, index):
        """
        Récupère la MAC du logement et publie l'index de consommation
        sur le topic ecocamp/<mac>/conso avec rétention (retain=True).
        """
        cursor = self.mysql.connection.cursor()
        try:
            cursor.execute(
                "SELECT adresse_mac, nom_hebergement FROM hebergement WHERE id_hebergement = %s",
                (id_h,)
            )
            row = cursor.fetchone()

            if row and row['adresse_mac']:
                mac = row['adresse_mac']
                nom = row['nom_hebergement']

                payload = {
                    "nom":    nom,
                    "type":   "Eau" if id_flux == 4 else "Elec",
                    "valeur": index,
                    "unite":  "L" if id_flux == 4 else "kWh",
                    "maj":    datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }

                if self.mqtt_client:
                    topic = f"ecocamp/{mac}/conso"
                    self.mqtt_client.publish(topic, json.dumps(payload), retain=True)
        finally:
            cursor.close()