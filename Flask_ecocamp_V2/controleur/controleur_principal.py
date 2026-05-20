from flask import render_template, request, jsonify, session, redirect, url_for, flash
from modele.Client import Client
from utils.publisher_v2 import LogementPublisher
from utils.publisher_v2 import DonneesPublisher
from utils.publisher_v2 import ConsommationsPublisher
from utils.publisher_v2 import MessagesPublisher
from utils.publisher_v2 import QuotaPublisher
from utils.publisher_v2 import EvenementsPublisher


def publier_tout():
    """Publie toutes les données sur le broker MQTT après une modification."""
    erreurs = []
    for label, cls in [
        ("logements",     LogementPublisher),
        ("consommations", ConsommationsPublisher),
        ("donnees",       DonneesPublisher),
        ("quotas",        QuotaPublisher),
        ("messages",      MessagesPublisher),
        ("evenements",    EvenementsPublisher),
    ]:
        try:
            cls().publier_tout()
        except Exception as e:
            erreurs.append(f"{label}: {e}")
    return erreurs


class controleur_principal:
    def __init__(self, appli):
        self.mysql = appli.mysql
        self.routes_exceptions = ['afficher_login', 'static', 'traiter_login']

    # ==========================================
    # --- AUTHENTIFICATION ---
    # ==========================================

    def afficher_login(self):
        return render_template("login.html")

    def afficher_index(self):
        return render_template("index.html")

    def traiter_login(self):
        try:
            data = request.json
            login = data["identifiant"]
            mdp = data["pwd"]
            client = Client(self.mysql)
            res = client.test_login(login, mdp)
            if res["valeur"] == 1:
                session.permanent = True
                session['client'] = login
            return jsonify(res)
        except Exception:
            return jsonify({"valeur": 0})

    def test_before_request(self):
        if request.endpoint and request.endpoint not in self.routes_exceptions:
            if not session.get("client"):
                return redirect(url_for('afficher_login'))

    def deconnexion(self):
        session.clear()
        return redirect(url_for('afficher_login'))

    # ==========================================
    # --- QUOTAS ---
    # ==========================================

    def afficher_quotas(self):
        client = Client(self.mysql)
        if request.method == 'POST':
            try:
                id_type = int(request.form.get("id_type_logement"))
                eau = float(request.form.get("quota_eau"))
                elec = float(request.form.get("quota_elec"))
                client.modifier_quota_type(id_type, eau, elec)
                flash("Quotas mis à jour avec succès !", "success")

                # Publie quotas + données (les quotas impactent l'affichage des consommations)
                erreurs = []
                for label, cls in [("quotas", QuotaPublisher), ("donnees", DonneesPublisher)]:
                    try:
                        cls().publier_tout()
                    except Exception as e:
                        erreurs.append(f"{label}: {e}")
                if erreurs:
                    flash(f"Quotas mis à jour mais erreur MQTT : {', '.join(erreurs)}", "error")

            except (ValueError, TypeError):
                flash("Erreur dans les valeurs saisies.", "error")
            return redirect(url_for('quotas'))

        types = client.get_types_logement()
        return render_template("quotas.html", types_logement=types)

    # ==========================================
    # --- CONSOMMATIONS ---
    # ==========================================

    def afficher_consommations(self):
        client = Client(self.mysql)
        hebergements = client.get_hebergements()
        id_h = request.args.get('id_hebergement')

        if not id_h and hebergements:
            premier_id = hebergements[0]['id_hebergement'] if isinstance(hebergements[0], dict) else hebergements[0][0]
            return redirect(url_for('consommations', id_hebergement=premier_id))

        conso = client.get_consommations_par_hebergement(id_h) if id_h else []
        return render_template(
            "consommations.html",
            consommations=conso,
            hebergements=hebergements,
            id_selectionne=id_h
        )

    # ==========================================
    # --- SÉJOURS ---
    # ==========================================

    def afficher_sejours(self):
        client = Client(self.mysql)
        liste_sejours = client.get_sejours()
        liste_h = client.get_hebergements()
        return render_template("sejours.html", sejours=liste_sejours, hebergements=liste_h)

    def enregistrer_sejour(self):
        client = Client(self.mysql)
        id_h = request.form.get("id_hebergement")
        debut = request.form.get("date_debut")
        fin = request.form.get("date_fin")

        if not debut or not fin:
            flash("Veuillez choisir des dates valides.", "error")
            return redirect(url_for('sejours'))

        if not client.logement_est_disponible(id_h, debut, fin):
            flash("Ce logement est déjà occupé pour ces dates !", "error")
            return redirect(url_for('sejours'))

        try:
            client.ajouter_sejour(id_h, debut, fin)
            flash("Séjour enregistré avec succès !", "success")

            # Publie tout : le séjour impacte quotas, données et logements
            erreurs = publier_tout()
            if erreurs:
                flash(f"Séjour enregistré mais erreurs MQTT : {', '.join(erreurs)}", "error")

        except Exception as e:
            flash(f"Une erreur est survenue : {e}", "error")

        return redirect(url_for('sejours'))

    def supprimer_sejour(self, id_sejour):
        client = Client(self.mysql)
        try:
            client.supprimer_sejour(id_sejour)
            flash("Séjour supprimé.", "success")

            erreurs = publier_tout()
            if erreurs:
                flash(f"Séjour supprimé mais erreurs MQTT : {', '.join(erreurs)}", "error")

        except Exception as e:
            flash(f"Erreur lors de la suppression : {e}", "error")
        return redirect(url_for('sejours'))

    # ==========================================
    # --- API SÉJOURS (sans rechargement) ---
    # ==========================================

    def api_enregistrer_sejour(self):
        """API pour enregistrer un séjour sans rechargement de page"""
        try:
            data = request.get_json()
            id_hebergement = data.get('id_hebergement')
            date_debut = data.get('date_debut')
            date_fin = data.get('date_fin')
            
            if not id_hebergement or not date_debut or not date_fin:
                return jsonify({"success": False, "message": "Veuillez remplir tous les champs"})
            
            client = Client(self.mysql)
            
            # Vérifier la disponibilité
            if not client.logement_est_disponible(id_hebergement, date_debut, date_fin):
                return jsonify({"success": False, "message": "Ce logement est déjà occupé pour ces dates"})
            
            # Ajouter le séjour
            client.ajouter_sejour(id_hebergement, date_debut, date_fin)
            
            # Publier les données MQTT
            erreurs = publier_tout()
            
            return jsonify({
                "success": True, 
                "message": "Séjour créé avec succès",
                "mqtt_errors": erreurs if erreurs else None
            })
            
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})

    def api_get_sejours(self):
        """API pour récupérer la liste des séjours (format JSON)"""
        try:
            client = Client(self.mysql)
            sejours = client.get_sejours()
            
            # Formater les dates pour JSON
            for s in sejours:
                if s.get('date_debut_sejour'):
                    s['date_debut_sejour'] = s['date_debut_sejour'].strftime('%Y-%m-%d')
                if s.get('date_fin_sejour'):
                    s['date_fin_sejour'] = s['date_fin_sejour'].strftime('%Y-%m-%d')
                # S'assurer que l'ID est un entier
                s['id_sejour'] = int(s['id_sejour']) if s.get('id_sejour') else 0
            
            return jsonify(sejours)
        except Exception as e:
            print(f"Erreur API get_sejours: {e}")
            return jsonify([])

    def api_supprimer_sejour(self, id_sejour):
        """API pour supprimer un séjour sans rechargement de page"""
        try:
            client = Client(self.mysql)
            client.supprimer_sejour(id_sejour)
            
            # Publier les données MQTT
            erreurs = publier_tout()
            
            return jsonify({
                "success": True, 
                "message": "Séjour supprimé avec succès",
                "mqtt_errors": erreurs if erreurs else None
            })
            
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})

    # ==========================================
    # --- PUBLICATION MQTT MANUELLE ---
    # ==========================================

    def publier_logements(self):
        """Publication manuelle de tous les logements."""
        try:
            LogementPublisher().publier_tout()
            flash("Logements publiés sur le broker MQTT.", "success")
        except Exception as e:
            flash(f"Erreur MQTT : {e}", "error")
        return redirect(url_for('sejours'))

    def publier_donnees(self):
        """Publication manuelle de toutes les données (consommations + historique 7j)."""
        try:
            ConsommationsPublisher().publier_tout()
            DonneesPublisher().publier_tout()
            flash("Données publiées sur le broker MQTT.", "success")
        except Exception as e:
            flash(f"Erreur MQTT : {e}", "error")
        return redirect(url_for('consommations'))

    # ==========================================
    # --- MESSAGES ---
    # ==========================================

    def afficher_messages(self):
        client = Client(self.mysql)
        messages = client.get_messages()
        types_message = client.get_types_message()
        return render_template("messages.html", messages=messages, types_message=types_message)

    def enregistrer_message(self):
        client = Client(self.mysql)
        try:
            contenu = request.form.get("contenu_message", "").strip()
            date_debut = request.form.get("date_debut_message")
            date_fin = request.form.get("date_fin_message")
            horaire = request.form.get("horaire_evenement_message") or None
            id_type = int(request.form.get("id_type_message"))

            if not contenu or not date_debut or not date_fin:
                flash("Veuillez remplir tous les champs obligatoires.", "error")
                return redirect(url_for('messages'))

            client.ajouter_message(contenu, date_debut, date_fin, horaire, id_type)
            flash("Message enregistré avec succès !", "success")

            # Publie messages ET évènements (le nouveau message peut être un évènement)
            erreurs = []
            for label, cls in [("messages", MessagesPublisher), ("evenements", EvenementsPublisher)]:
                try:
                    cls().publier_tout()
                except Exception as e:
                    erreurs.append(f"{label}: {e}")
            if erreurs:
                flash(f"Message enregistré mais erreurs MQTT : {', '.join(erreurs)}", "error")

        except Exception as e:
            flash(f"Une erreur est survenue : {e}", "error")
        return redirect(url_for('messages'))

    def supprimer_message(self, id_message):
        client = Client(self.mysql)
        try:
            client.supprimer_message(id_message)
            flash("Message supprimé.", "success")

            erreurs = []
            for label, cls in [("messages", MessagesPublisher), ("evenements", EvenementsPublisher)]:
                try:
                    cls().publier_tout()
                except Exception as e:
                    erreurs.append(f"{label}: {e}")
            if erreurs:
                flash(f"Message supprimé mais erreurs MQTT : {', '.join(erreurs)}", "error")

        except Exception as e:
            flash(f"Erreur lors de la suppression : {e}", "error")
        return redirect(url_for('messages'))

    # ==========================================
    # --- ERREURS ---
    # ==========================================

    def page_not_found(self, e):
        return render_template('404.html'), 404
