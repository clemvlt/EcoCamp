
# Import des modules nécessaires pour Flask et la gestion des requêtes HTTP
from flask import render_template, request, jsonify, session, redirect, url_for, flash
from modele.Client import Client  # Module pour interagir avec la base de données
from utils.publisher_logements import LogementPublisher  # Publie les informations des logements via MQTT
from utils.publisher_donnees import DonneesPublisher  # Publie les données de consommation via MQTT
from utils.publisher_messages import MessagesPublisher  # Publie les messages via MQTT
from utils.publisher_quota import QuotaPublisher  # Publie les quotas via MQTT

class controleur_principal:
    def __init__(self, appli):
        """Initialise le contrôleur avec la connexion MySQL et les routes autorisées sans authentification."""
        self.mysql = appli.mysql  # Connexion MySQL partagée avec l'application Flask
        # Routes accessibles sans être connecté (ex: login, fichiers statiques)
        self.routes_exceptions = ['afficher_login', 'static', 'traiter_login']

    # ==========================================
    # --- AUTHENTIFICATION ---
    # ==========================================

    def afficher_login(self):
        """Affiche la page de connexion (login.html)."""
        return render_template("login.html")  # Rend le template de connexion

    def afficher_index(self):
        """Affiche la page d'accueil (index.html)."""
        return render_template("index.html")  # Rend le template d'accueil

    def traiter_login(self):
        """Traite la requête de connexion : vérifie les identifiants et crée une session si valide."""
        try:
            data = request.json  # Récupère les données JSON envoyées par le client
            login = data["identifiant"]  # Identifiant saisi par l'utilisateur
            mdp = data["pwd"]  # Mot de passe saisi

            client = Client(self.mysql)  # Crée une instance du client pour interagir avec la base
            res = client.test_login(login, mdp)  # Vérifie les identifiants en base

            if res["valeur"] == 1:  # Si l'authentification réussit
                session.permanent = True  # Session permanente
                session['client'] = login  # Stocke l'identifiant dans la session

            return jsonify(res)  # Retourne le résultat sous forme JSON
        except Exception:
            # En cas d'erreur (ex: données manquantes), retourne un échec
            return jsonify({"valeur": 0})

    def test_before_request(self):
        """
        Middleware Flask : vérifie si l'utilisateur est connecté avant chaque requête.
        Redirige vers la page de login si non connecté et que la route n'est pas une exception.
        """
        # Vérifie si la route actuelle n'est pas dans les exceptions (ex: login)
        if request.endpoint and request.endpoint not in self.routes_exceptions:
            if not session.get("client"):  # Si l'utilisateur n'est pas connecté
                return redirect(url_for('afficher_login'))  # Redirige vers le login

    def deconnexion(self):
        """Déconnecte l'utilisateur en vidant la session et redirige vers le login."""
        session.clear()  # Supprime toutes les données de session
        return redirect(url_for('afficher_login'))  # Redirige vers la page de login

    # ==========================================
    # --- QUOTAS ---
    # ==========================================

    def afficher_quotas(self):
        """Affiche la page des quotas et traite la mise à jour des quotas par type de logement."""
        client = Client(self.mysql)  # Instance pour interagir avec la base

        if request.method == 'POST':  # Si le formulaire de mise à jour est soumis
            try:
                # Récupère les valeurs du formulaire
                id_type = int(request.form.get("id_type_logement"))  # ID du type de logement
                eau = float(request.form.get("quota_eau"))  # Quota d'eau
                elec = float(request.form.get("quota_elec"))  # Quota d'électricité

                # Met à jour les quotas en base
                client.modifier_quota_type(id_type, eau, elec)
                flash("Quotas mis à jour avec succès !", "success")  # Message de succès

                # Publie les nouveaux quotas via MQTT
                try:
                    QuotaPublisher().publier_tout()  # Publie tous les quotas
                except Exception as e:
                    # Affiche un message d'erreur si la publication MQTT échoue
                    flash(f"Quotas mis à jour mais erreur MQTT : {e}", "error")

            except (ValueError, TypeError):
                # Erreur si les valeurs ne sont pas valides (ex: non numériques)
                flash("Erreur dans les valeurs saisies.", "error")
            return redirect(url_for('quotas'))  # Recharge la page des quotas

        # Si GET, récupère les types de logement pour afficher le formulaire
        types = client.get_types_logement()
        return render_template("quotas.html", types_logement=types)  # Affiche la page avec les types

    # ==========================================
    # --- CONSOMMATIONS ---
    # ==========================================

    def afficher_consommations(self):
        """
        Affiche les relevés de consommation filtrés par hébergement.
        Si aucun logement n'est sélectionné, redirige vers le premier logement disponible.
        """
        client = Client(self.mysql)
        hebergements = client.get_hebergements()  # Liste de tous les hébergements
        id_h = request.args.get('id_hebergement')  # ID de l'hébergement sélectionné

        # Si aucun hébergement n'est sélectionné, redirige vers le premier
        if not id_h and hebergements:
            # Récupère l'ID du premier hébergement (gère les deux formats de résultat possible)
            premier_id = hebergements[0]['id_hebergement'] if isinstance(hebergements[0], dict) else hebergements[0][0]
            return redirect(url_for('consommations', id_hebergement=premier_id))

        # Récupère les consommations pour l'hébergement sélectionné
        conso = client.get_consommations_par_hebergement(id_h) if id_h else []

        return render_template(
            "consommations.html",
            consommations=conso,  # Données de consommation
            hebergements=hebergements,  # Liste des hébergements pour le filtre
            id_selectionne=id_h  # ID de l'hébergement actuellement sélectionné
        )

    # ==========================================
    # --- SÉJOURS ---
    # ==========================================

    def afficher_sejours(self):
        """Affiche la liste des séjours et le formulaire pour en créer un nouveau."""
        client = Client(self.mysql)
        liste_sejours = client.get_sejours()  # Récupère tous les séjours
        liste_h = client.get_hebergements()  # Récupère tous les hébergements
        return render_template(
            "sejours.html",
            sejours=liste_sejours,  # Liste des séjours pour l'affichage
            hebergements=liste_h  # Liste des hébergements pour le formulaire
        )

    def enregistrer_sejour(self):
        """Vérifie la disponibilité du logement et crée un nouveau séjour."""
        client = Client(self.mysql)
        id_h = request.form.get("id_hebergement")  # ID de l'hébergement
        debut = request.form.get("date_debut")  # Date de début du séjour
        fin = request.form.get("date_fin")  # Date de fin du séjour

        # Vérifie que les dates sont fournies
        if not debut or not fin:
            flash("Veuillez choisir des dates valides.", "error")
            return redirect(url_for('sejours'))

        # Vérifie que le logement est disponible pour les dates demandées
        if not client.logement_est_disponible(id_h, debut, fin):
            flash("Ce logement est déjà occupé pour ces dates !", "error")
            return redirect(url_for('sejours'))

        try:
            client.ajouter_sejour(id_h, debut, fin)  # Crée le séjour en base
            flash("Séjour enregistré avec succès !", "success")

            # Publie les mises à jour via MQTT
            try:
                QuotaPublisher().publier_tout()  # Met à jour les quotas
                DonneesPublisher().publier_tout()  # Met à jour les données
            except Exception as e:
                flash(f"Séjour enregistré mais erreur MQTT : {e}", "error")

        except Exception as e:
            flash(f"Une erreur est survenue : {e}", "error")

        return redirect(url_for('sejours'))  # Recharge la page des séjours

    def supprimer_sejour(self, id_sejour):
        """Supprime un séjour et ses données associées (historique, quotas)."""
        client = Client(self.mysql)
        try:
            client.supprimer_sejour(id_sejour)  # Supprime le séjour en base
            flash("Séjour supprimé.", "success")

            # Publie les mises à jour via MQTT
            try:
                QuotaPublisher().publier_tout()  # Met à jour les quotas
                DonneesPublisher().publier_tout()  # Met à jour les données
            except Exception as e:
                flash(f"Séjour supprimé mais erreur MQTT : {e}", "error")

        except Exception as e:
            flash(f"Erreur lors de la suppression : {e}", "error")
        return redirect(url_for('sejours'))  # Recharge la page des séjours

    # ==========================================
    # --- PUBLICATION MQTT LOGEMENTS ---
    # ==========================================

    def publier_logements(self):
        """Publie la liste des logements avec leur adresse MAC via MQTT."""
        try:
            publisher = LogementPublisher()  # Instance pour publier les logements
            logements = publisher.get_logements()  # Récupère les logements depuis la base
            if not logements:
                flash("Aucun logement trouvé en base.", "error")
                return redirect(url_for('sejours'))
            publisher.publier_par_logement(logements)  # Publie chaque logement via MQTT
            flash(f"{len(logements)} logement(s) publiés sur le broker MQTT.", "success")
        except Exception as e:
            flash(f"Erreur lors de la publication MQTT : {e}", "error")
        return redirect(url_for('sejours'))  # Retour à la page des séjours

    # ==========================================
    # --- PUBLICATION MQTT DONNÉES (historique 7j) ---
    # ==========================================

    def publier_donnees(self):
        """
        Publie les données de consommation (index courant, historique des 7 derniers jours)
        pour tous les hébergements via MQTT.
        """
        try:
            publisher = DonneesPublisher()  # Instance pour publier les données
            donnees = publisher.get_donnees()  # Récupère les données depuis la base
            if not donnees:
                flash("Aucun hébergement avec adresse MAC trouvé.", "error")
                return redirect(url_for('consommations'))
            nb = publisher.publier_par_donnees(donnees)  # Publie les données via MQTT
            flash(
                f"{nb} hébergement(s) publiés avec leur historique 7 jours sur le broker MQTT.",
                "success",
            )
        except Exception as e:
            flash(f"Erreur lors de la publication MQTT des données : {e}", "error")
        return redirect(url_for('consommations'))  # Retour à la page des consommations

    # ==========================================
    # --- MESSAGES ---
    # ==========================================

    def afficher_messages(self):
        """Affiche la page des messages avec l'historique et le formulaire de création."""
        client = Client(self.mysql)
        messages = client.get_messages()  # Récupère tous les messages
        types_message = client.get_types_message()  # Récupère les types de messages
        return render_template(
            "messages.html",
            messages=messages,  # Liste des messages pour l'affichage
            types_message=types_message  # Types de messages pour le formulaire
        )

    def enregistrer_message(self):
        """Enregistre un nouveau message en base de données."""
        client = Client(self.mysql)
        try:
            # Récupère les données du formulaire
            contenu = request.form.get("contenu_message", "").strip()  # Contenu du message
            date_debut = request.form.get("date_debut_message")  # Date de début d'affichage
            date_fin = request.form.get("date_fin_message")  # Date de fin d'affichage
            horaire = request.form.get("horaire_evenement_message") or None  # Horaire (optionnel)
            id_type = int(request.form.get("id_type_message"))  # Type de message

            # Vérifie que les champs obligatoires sont remplis
            if not contenu or not date_debut or not date_fin:
                flash("Veuillez remplir tous les champs obligatoires.", "error")
                return redirect(url_for('messages'))

            # Enregistre le message en base
            client.ajouter_message(contenu, date_debut, date_fin, horaire, id_type)
            flash("Message enregistré avec succès !", "success")

            # Publie le message via MQTT
            try:
                MessagesPublisher().publier_tout()  # Publie tous les messages
            except Exception as e:
                flash(f"Message enregistré mais erreur MQTT : {e}", "error")

        except Exception as e:
            flash(f"Une erreur est survenue : {e}", "error")
        return redirect(url_for('messages'))  # Recharge la page des messages

    def supprimer_message(self, id_message):
        """Supprime un message par son ID."""
        client = Client(self.mysql)
        try:
            client.supprimer_message(id_message)  # Supprime le message en base
            flash("Message supprimé.", "success")

            # Publie la mise à jour via MQTT
            try:
                MessagesPublisher().publier_tout()  # Met à jour les messages publiés
            except Exception as e:
                flash(f"Message supprimé mais erreur MQTT : {e}", "error")

        except Exception as e:
            flash(f"Erreur lors de la suppression : {e}", "error")
        return redirect(url_for('messages'))  # Recharge la page des messages

    # ==========================================
    # --- ERREURS ---
    # ==========================================

    def page_not_found(self, e):
        """Affiche une page d'erreur 404 personnalisée."""
        return render_template('404.html'), 404  # Rend le template 404 avec le code HTTP 404
