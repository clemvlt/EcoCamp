# Dans controleur_principal.py
from flask import render_template, request, jsonify, session, redirect, url_for
from modele.Client import Client 

class ControleurPrincipal:
    def __init__(self, appli):
        """
        Initialise le contrôleur avec l'accès à MySQL et définit les pages 
        accessibles sans être connecté.
        """
        self.mysql = appli.mysql
        # Liste des routes qui ne nécessitent pas de vérification de session (login, etc.)
        self.routes_exceptions=['afficher_login', 'static', 'traiter_login']

    def afficher_login(self):
        """Affiche la page de connexion."""
        return render_template("login.html")

    def afficher_index(self):
        """Affiche la page d'accueil (Tableau de bord)."""
        return render_template("index.html")

    def traiter_login(self):
        """
        Récupère les identifiants envoyés en JSON, interroge le modèle Client
        et crée une session si l'utilisateur existe.
        """
        data = request.json
        login = data["identifiant"]
        mdp = data["pwd"]

        client = Client(self.mysql)
        res = client.test_login(login, mdp)

        # Si le modèle retourne 1, l'admin est reconnu
        if res["valeur"] == 1:
            session.permanent = True # La session survit à la fermeture du navigateur
            session['client'] = login # On stocke le login en session

        return jsonify(res)

    def test_before_request(self):
        """
        Système de sécurité : vérifie avant chaque page si l'utilisateur est connecté.
        Si aucune session n'est trouvée, redirection vers le login.
        """
        if request.endpoint and request.endpoint not in self.routes_exceptions: 
            if not session.get("client"):
                return redirect(url_for('afficher_login'))

    def deconnexion(self):
        """Vide la session et renvoie au login."""
        session.clear()  
        return redirect(url_for('afficher_login'))

    # ==========================================
    # --- LOGIQUE DES QUOTAS ---
    # ==========================================

    def afficher_quotas(self):
        """
        Gère à la fois l'affichage de la page Quotas (GET) 
        et la réception du formulaire de modification (POST).
        """
        client = Client(self.mysql)
        
        # Si l'utilisateur a cliqué sur "Mettre à jour"
        if request.method == 'POST':
            try:
                # Récupération des données du formulaire HTML
                id_type = int(request.form.get("id_type_logement"))
                eau = float(request.form.get("quota_eau"))
                elec = float(request.form.get("quota_elec"))
                
                # Envoi des nouvelles valeurs au modèle Client
                client.modifier_quota_type(id_type, eau, elec)
            except (ValueError, TypeError) as e:
                print(f"Erreur de conversion de données : {e}")
            
            # Après modification, on recharge la page pour voir les changements
            return redirect(url_for('quotas'))

        # Si simple visite de la page : on récupère la liste pour remplir le tableau
        types = client.get_types_logement() 
        return render_template("quotas.html", types_logement=types)

    # ==========================================
    # ---  CONSOMMATIONS ---
    # ==========================================

    def afficher_consommations(self):
        """
        Affiche la liste des relevés. Permet le filtrage par hébergement 
        via un paramètre dans l'URL (?id_hebergement=X).
        """
        client = Client(self.mysql)
        id_h = request.args.get('id_hebergement') # Récupère le choix du menu déroulant
        
        hebergements = client.get_hebergements()
        
        # Filtrage selon si un hébergement est sélectionné ou non
        if id_h:
            conso = client.get_consommations_par_hebergement(id_h)
        else:
            conso = client.get_consommations()

        return render_template("consommations.html", 
                            consommations=conso, 
                            hebergements=hebergements, 
                            id_selectionne=id_h)

    # ==========================================
    # --- LOGIQUE DES SÉJOURS ---
    # ==========================================

    def afficher_sejours(self):
        """Affiche la liste des séjours enregistrés et la liste des hébergements pour le formulaire."""
        client = Client(self.mysql)
        liste_sejours = client.get_sejours()
        liste_h = client.get_hebergements()
        
        return render_template("sejours.html", 
                               sejours=liste_sejours, 
                               hebergements=liste_h)

    def enregistrer_sejour(self):
        """Récupère les infos du formulaire et crée un nouveau séjour."""
        id_h = request.form.get("id_hebergement")
        debut = request.form.get("date_debut")
        fin = request.form.get("date_fin")
        
        client = Client(self.mysql)
        # On appelle ajouter_sejour qui s'occupe de figer les index de départ
        client.ajouter_sejour(id_h, debut, fin)
        return redirect(url_for('afficher_sejours'))
    
    def supprimer_sejour(self, id_sejour):
        """
        Supprime un séjour et toutes ses données liées (historique et quotas)
        puis redirige l'utilisateur vers la liste.
        """
        cursor = self.mysql.connection.cursor()
        try:
            # 1. On vide les tables "enfants" d'abord pour éviter les erreurs de clé étrangère
            # On supprime les consommations liées au séjour
            cursor.execute("DELETE FROM historique_cosommation WHERE id_sejour = %s", (id_sejour,))
            
            # On supprime les quotas liés au séjour
            cursor.execute("DELETE FROM quota WHERE id_sejour = %s", (id_sejour,))
            
            # 2. Une fois les liens coupés, on supprime le séjour (le parent)
            cursor.execute("DELETE FROM sejour WHERE id_sejour = %s", (id_sejour,))
            
            # On valide la transaction SQL
            self.mysql.connection.commit()
            
            # --- LE CORRECTIF EST ICI ---
            # On redirige vers la page des séjours pour rafraîchir la liste
            return redirect(url_for('afficher_sejours'))
        
        except Exception as e:
            # En cas d'erreur, on annule tout (rollback) pour rester cohérent
            self.mysql.connection.rollback()
            print(f"Erreur lors de la suppression : {e}")
            # On redirige aussi en cas d'erreur pour éviter le TypeError
            return redirect(url_for('afficher_sejours'))
        finally:
            cursor.close()
    def afficher_messages(self):
        """Affiche la page des messages/alertes."""
        return render_template("messages.html")

    # ==========================================
    # --- LOGIQUE DES COMPTEURS ---
    # ==========================================

    def enregistrer_releve(self, id_h, id_flux, nouvel_index):
        """
        Méthode critique : 
        1. Ajoute une ligne dans l'historique (consommation)
        2. Met à jour la valeur actuelle dans la table 'compteur'
        """
        cursor = self.mysql.connection.cursor()
        try:
            # Enregistrement de la trace historique
            cursor.execute("""
                INSERT INTO consommation (index_consommation, id_type_flux, id_hebergement) 
                VALUES (%s, %s, %s)
            """, (nouvel_index, id_flux, id_h))
            
            # Mise à jour de la valeur "temps réel"
            cursor.execute("""
                UPDATE compteur SET index_compteur = %s 
                WHERE id_hebergement = %s AND id_type_flux = %s
            """, (nouvel_index, id_h, id_flux))
            
            self.mysql.connection.commit() # On valide les deux opérations en même temps
        except Exception as e:
            self.mysql.connection.rollback() # Si l'une échoue, on annule tout
            print(f"Erreur lors de l'enregistrement du relevé : {e}")
        finally:
            cursor.close()