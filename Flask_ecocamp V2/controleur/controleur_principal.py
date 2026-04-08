from flask import render_template, request, jsonify, session, redirect, url_for, flash
from modele.Client import Client
from utils.publisher_logements import LogementPublisher


class controleur_principal:
    def __init__(self, appli):
        self.mysql = appli.mysql
        self.routes_exceptions = ['afficher_login', 'static', 'traiter_login']

    # ==========================================
    # --- AUTHENTIFICATION ---
    # ==========================================

    def afficher_login(self):
        """Affiche la page de connexion."""
        return render_template("login.html")

    def afficher_index(self):
        """Affiche la page d'accueil."""
        return render_template("index.html")

    def traiter_login(self):
        """Reçoit les identifiants en JSON, vérifie en base et crée la session."""
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
        except Exception as e:
            return jsonify({"valeur": 0})

    def test_before_request(self):
        """Redirige vers le login si l'utilisateur n'est pas connecté."""
        if request.endpoint and request.endpoint not in self.routes_exceptions:
            if not session.get("client"):
                return redirect(url_for('afficher_login'))

    def deconnexion(self):
        """Vide la session et redirige vers le login."""
        session.clear()
        return redirect(url_for('afficher_login'))

    # ==========================================
    # --- QUOTAS ---
    # ==========================================

    def afficher_quotas(self):
        """Affiche et met à jour les quotas journaliers par catégorie de logement."""
        client = Client(self.mysql)

        if request.method == 'POST':
            try:
                id_type = int(request.form.get("id_type_logement"))
                eau = float(request.form.get("quota_eau"))
                elec = float(request.form.get("quota_elec"))
                client.modifier_quota_type(id_type, eau, elec)
                flash("Quotas mis à jour avec succès !", "success")
            except (ValueError, TypeError):
                flash("Erreur dans les valeurs saisies.", "error")
            return redirect(url_for('quotas'))

        types = client.get_types_logement()
        return render_template("quotas.html", types_logement=types)

    # ==========================================
    # --- CONSOMMATIONS ---
    # ==========================================

    def afficher_consommations(self):
        """
        Affiche les relevés filtrés par hébergement.
        Si aucun logement n'est sélectionné, redirige automatiquement
        vers le premier logement disponible.
        """
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
        """Affiche la liste des séjours et le formulaire de création."""
        client = Client(self.mysql)
        liste_sejours = client.get_sejours()
        liste_h = client.get_hebergements()
        return render_template("sejours.html", sejours=liste_sejours, hebergements=liste_h)

    def enregistrer_sejour(self):
        """Vérifie la disponibilité du logement et crée le séjour."""
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
        except Exception as e:
            flash(f"Une erreur est survenue : {e}", "error")

        return redirect(url_for('sejours'))

    def supprimer_sejour(self, id_sejour):
        """Supprime un séjour (historique et quotas supprimés via CASCADE)."""
        client = Client(self.mysql)
        try:
            client.supprimer_sejour(id_sejour)
            flash("Séjour supprimé.", "success")
        except Exception as e:
            flash(f"Erreur lors de la suppression : {e}", "error")
        return redirect(url_for('sejours'))

    # ==========================================
    # --- PUBLICATION MQTT LOGEMENTS ---
    # ==========================================

    def publier_logements(self):
        """Déclenche la publication MQTT de la liste des logements avec leur MAC."""
        try:
            publisher = LogementPublisher()
            logements = publisher.get_logements()
            if not logements:
                flash("Aucun logement trouvé en base.", "error")
                return redirect(url_for('sejours'))
            publisher.publier_par_logement(logements)
            flash(f"{len(logements)} logement(s) publiés sur le broker MQTT.", "success")
        except Exception as e:
            flash(f"Erreur lors de la publication MQTT : {e}", "error")
        return redirect(url_for('sejours'))

    # ==========================================
    # --- MESSAGES ---
    # ==========================================

    def afficher_messages(self):
        """Affiche la page des messages et l'historique depuis la base."""
        client = Client(self.mysql)
        messages = client.get_messages()
        types_message = client.get_types_message()
        return render_template("messages.html", messages=messages, types_message=types_message)

    def enregistrer_message(self):
        """Enregistre un nouveau message en base."""
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
        except Exception as e:
            flash(f"Une erreur est survenue : {e}", "error")
        return redirect(url_for('messages'))

    def supprimer_message(self, id_message):
        """Supprime un message par son ID."""
        client = Client(self.mysql)
        try:
            client.supprimer_message(id_message)
            flash("Message supprimé.", "success")
        except Exception as e:
            flash(f"Erreur lors de la suppression : {e}", "error")
        return redirect(url_for('messages'))

    # ==========================================
    # --- ERREURS ---
    # ==========================================

    def page_not_found(self, e):
        """Affiche la page d'erreur 404."""
        return render_template('404.html'), 404