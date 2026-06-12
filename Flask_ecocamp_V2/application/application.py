
# Import des modules nécessaires pour Flask et la gestion de la base de données MySQL
from flask import Flask  # Framework web pour créer l'application
from controleur.controleur_principal import controleur_principal  # Contrôleur principal pour gérer les routes
from flask_mysqldb import MySQL  # Extension Flask pour interagir avec MySQL
from datetime import timedelta  # Pour gérer la durée de vie des sessions

class Application:
    """
    Classe principale qui initialise Flask, MySQL et le contrôleur.
    Elle configure les routes et lance l'application.
    """

    def __init__(self):
        """
        Initialise l'application Flask, configure MySQL et le contrôleur principal.
        Définit également les dossiers pour les templates et les fichiers statiques.
        """
        # Chemins vers les dossiers de templates et de fichiers statiques
        template_dir = "../templates"  # Dossier contenant les templates HTML
        static_dir = "../static"  # Dossier contenant les fichiers statiques (CSS, JS, images)

        # Initialisation de l'application Flask
        self.app = Flask(
            __name__,
            template_folder=template_dir,  # Chemin vers les templates
            static_folder=static_dir,  # Chemin vers les fichiers statiques
            instance_relative_config=True  # Charge la configuration depuis le dossier instance
        )

        # Charge la configuration depuis le fichier config.cfg
        self.app.config.from_pyfile("/app/instance/config.cfg")

        # Configure la durée de vie des sessions permanentes
        self.app.permanent_session_lifetime = timedelta(
            seconds=self.app.config['PERMANT_SESSION_LIFETIME']  # Durée en secondes définie dans config.cfg
        )

        # Initialisation de l'extension MySQL pour Flask
        self.mysql = MySQL()  # Crée une instance de MySQL
        self.mysql.init_app(self.app)  # Associe MySQL à l'application Flask

        # Initialisation du contrôleur principal
        self.cp = controleur_principal(self)  # Passe l'instance de l'application au contrôleur
        self.__routage()  # Appelle la méthode pour configurer les routes

    def __routage(self):
        """Enregistre toutes les routes de l'application Flask."""

        # Middleware : vérifie si l'utilisateur est connecté avant chaque requête
        self.app.before_request(self.cp.test_before_request)

        # Gestionnaire d'erreur pour les pages non trouvées (404)
        self.app.register_error_handler(404, self.cp.page_not_found)

        # ==========================================
        # --- AUTHENTIFICATION ---
        # ==========================================

        # Route pour la page de connexion (GET)
        self.app.add_url_rule(
            "/",  # URL racine
            view_func=self.cp.afficher_login,  # Fonction qui gère la requête
            methods=["GET"]  # Méthode HTTP autorisée
        )

        # Route pour traiter la connexion (POST)
        self.app.add_url_rule(
            "/test_login",
            view_func=self.cp.traiter_login,
            methods=["POST"]
        )

        # Route pour la déconnexion (GET)
        self.app.add_url_rule(
            "/deconnexion",
            view_func=self.cp.deconnexion,
            methods=["GET"]
        )

        # ==========================================
        # --- PAGES PRINCIPALES ---
        # ==========================================

        # Route pour la page d'accueil (GET)
        self.app.add_url_rule(
            "/index",
            endpoint="index",  # Nom unique pour identifier la route
            view_func=self.cp.afficher_index,
            methods=["GET"]
        )

        # Route pour la page des séjours (GET)
        self.app.add_url_rule(
            "/sejours",
            endpoint="sejours",
            view_func=self.cp.afficher_sejours,
            methods=["GET"]
        )

        # Route pour la page des quotas (GET et POST)
        self.app.add_url_rule(
            "/quotas",
            endpoint="quotas",
            view_func=self.cp.afficher_quotas,
            methods=["GET", "POST"]  # Autorise les deux méthodes pour gérer le formulaire
        )

        # Route pour la page des consommations (GET)
        self.app.add_url_rule(
            "/consommations",
            endpoint="consommations",
            view_func=self.cp.afficher_consommations,
            methods=["GET"]
        )

        # Route pour la page des messages (GET)
        self.app.add_url_rule(
            "/messages",
            endpoint="messages",
            view_func=self.cp.afficher_messages,
            methods=["GET"]
        )

        # ==========================================
        # --- ACTIONS SÉJOURS ---
        # ==========================================

        # Route pour enregistrer un nouveau séjour (POST)
        self.app.add_url_rule(
            "/enregistrer_sejour",
            view_func=self.cp.enregistrer_sejour,
            methods=["POST"]
        )

        # Route pour supprimer un séjour (GET avec paramètre id_sejour)
        self.app.add_url_rule(
            "/supprimer_sejour/<int:id_sejour>",  # <int:id_sejour> capture un entier dans l'URL
            view_func=self.cp.supprimer_sejour,
            methods=["GET"]
        )

        # ==========================================
        # --- PUBLICATION MQTT LOGEMENTS ---
        # ==========================================

        # Route pour publier les logements via MQTT (POST)
        self.app.add_url_rule(
            "/publier_logements",
            endpoint="publier_logements",
            view_func=self.cp.publier_logements,
            methods=["POST"]
        )

        # ==========================================
        # --- ACTIONS MESSAGES ---
        # ==========================================

        # Route pour enregistrer un nouveau message (POST)
        self.app.add_url_rule(
            "/enregistrer_message",
            view_func=self.cp.enregistrer_message,
            methods=["POST"]
        )

        # Route pour supprimer un message (GET avec paramètre id_message)
        self.app.add_url_rule(
            "/supprimer_message/<int:id_message>",  # <int:id_message> capture un entier dans l'URL
            view_func=self.cp.supprimer_message,
            methods=["GET"]
        )

    def run(self):
        """Lance l'application Flask en mode développement."""
        self.app.run()  # Démarre le serveur web Flask
