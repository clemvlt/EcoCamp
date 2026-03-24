# Dans controleur_principal.py
from flask import render_template, request, jsonify, session, redirect, url_for
from modele.Client import Client 

class ControleurPrincipal:
    def __init__(self, appli):
        self.mysql = appli.mysql
        self.routes_exceptions=['afficher_login','static','traiter_login']

    def afficher_login(self):
        return render_template("login.html")

    def afficher_index(self):
        return render_template("index.html")

    def traiter_login(self):
        data = request.json
        login = data["identifiant"]
        mdp = data["pwd"]

        client = Client(self.mysql)
        res = client.test_login(login, mdp)

        if res["valeur"] == 1:
            session.permanent = True
            session['client'] = login

        return jsonify(res)

    def test_before_request(self):
        if request.endpoint and request.endpoint not in self.routes_exceptions: 
            if not session.get("client"):
                return redirect(url_for('afficher_login'))

    def deconnexion(self):
        session.clear()  
        return redirect(url_for('afficher_login'))

    # --- NOUVELLE LOGIQUE QUOTAS ---
    def afficher_quotas(self):
        client = Client(self.mysql)
        
        if request.method == 'POST':
            # On récupère les données et on les convertit immédiatement
            try:
                id_type = int(request.form.get("id_type_logement"))
                eau = float(request.form.get("quota_eau"))
                elec = float(request.form.get("quota_elec"))
                
                # Appel au modèle
                client.modifier_quota_type(id_type, eau, elec)
            except (ValueError, TypeError) as e:
                print(f"Erreur de conversion de données : {e}")
                
            return redirect(url_for('quotas'))

        types = client.get_types_logement() 
        return render_template("quotas.html", types_logement=types)

    def update_quotas(self):
        id_type = request.form.get("id_type_logement")
        eau = request.form.get("quota_eau")
        elec = request.form.get("quota_elec")
        
        client = Client(self.mysql)
        client.modifier_quota_type(id_type, eau, elec)
        return redirect(url_for('afficher_quotas'))

    # --- CONSOMMATIONS ---
    def afficher_consommations(self):
        client = Client(self.mysql)
        id_h = request.args.get('id_hebergement')
        
        hebergements = client.get_hebergements()
        
        # On récupère les consommations filtrées ou globales
        if id_h:
            conso = client.get_consommations_par_hebergement(id_h)
        else:
            conso = client.get_consommations()

        return render_template("consommations.html", 
                            consommations=conso, 
                            hebergements=hebergements, 
                            id_selectionne=id_h)

    # --- SEJOURS ---
    def afficher_sejours(self):
        client = Client(self.mysql)
        liste_sejours = client.get_sejours()
        liste_h = client.get_hebergements()
        
        return render_template("sejours.html", 
                               sejours=liste_sejours, 
                               hebergements=liste_h)

    def enregistrer_sejour(self):
        id_h = request.form.get("id_hebergement")
        debut = request.form.get("date_debut")
        fin = request.form.get("date_fin")
        
        client = Client(self.mysql)
        # La méthode ajouter_sejour doit maintenant exploiter la table compteur
        # pour figer les index de départ comme discuté.
        client.ajouter_sejour(id_h, debut, fin)
        return redirect(url_for('afficher_sejours'))
    
    def supprimer_sejour(self, id_sejour):
        client = Client(self.mysql)
        client.supprimer_sejour(id_sejour)
        return redirect(url_for('afficher_sejours'))

    # --- MESSAGES ---
    def afficher_messages(self):
        return render_template("messages.html")

    # --- COMPTEURS ET RELEVES ---
    def enregistrer_releve(self, id_h, id_flux, nouvel_index):
        cursor = self.mysql.connection.cursor()
        try:
            # 1. Ajout dans l'historique consommation
            cursor.execute("""
                INSERT INTO consommation (index_consommation, id_type_flux, id_hebergement) 
                VALUES (%s, %s, %s)
            """, (nouvel_index, id_flux, id_h))
            
            # 2. Mise à jour de la table compteur (Source de vérité)
            cursor.execute("""
                UPDATE compteur SET index_compteur = %s 
                WHERE id_hebergement = %s AND id_type_flux = %s
            """, (nouvel_index, id_h, id_flux))
            
            self.mysql.connection.commit()
        except Exception as e:
            self.mysql.connection.rollback()
            print(f"Erreur lors de l'enregistrement du relevé : {e}")
        finally:
            cursor.close()