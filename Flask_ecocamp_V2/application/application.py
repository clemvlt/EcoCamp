import os
from flask import Flask
from controleur.controleur_principal import controleur_principal
from flask_mysqldb import MySQL
from datetime import timedelta


class Application:
    """
    Instancie Flask, MySQL et ControleurPrincipal.
    Crée les routes et lance l'application.
    """
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")

        self.app = Flask(
            __name__,
            template_folder=template_dir,
            static_folder=static_dir,
            instance_relative_config=True
        )
        self.app.config.from_pyfile("config.cfg")
        self.app.permanent_session_lifetime = timedelta(
            seconds=self.app.config['PERMANT_SESSION_LIFETIME']
        )

        self.mysql = MySQL()
        self.mysql.init_app(self.app)

        self.cp = controleur_principal(self)
        self.__routage()

    def __routage(self):
        """Enregistrement de toutes les routes de l'application."""
        self.app.before_request(self.cp.test_before_request)

        # Erreur 404
        self.app.register_error_handler(404, self.cp.page_not_found)

        # Authentification
        self.app.add_url_rule("/", view_func=self.cp.afficher_login, methods=["GET"])
        self.app.add_url_rule("/test_login", view_func=self.cp.traiter_login, methods=["POST"])
        self.app.add_url_rule("/deconnexion", view_func=self.cp.deconnexion, methods=["GET"])

        # Pages principales
        self.app.add_url_rule("/index", endpoint="index", view_func=self.cp.afficher_index, methods=["GET"])
        self.app.add_url_rule("/sejours", endpoint="sejours", view_func=self.cp.afficher_sejours, methods=["GET"])
        self.app.add_url_rule("/quotas", endpoint="quotas", view_func=self.cp.afficher_quotas, methods=["GET", "POST"])
        self.app.add_url_rule("/consommations", endpoint="consommations", view_func=self.cp.afficher_consommations, methods=["GET"])
        self.app.add_url_rule("/messages", endpoint="messages", view_func=self.cp.afficher_messages, methods=["GET"])

        # Actions séjours (rechargement classique)
        self.app.add_url_rule("/enregistrer_sejour", view_func=self.cp.enregistrer_sejour, methods=["POST"])
        self.app.add_url_rule("/supprimer_sejour/<int:id_sejour>", view_func=self.cp.supprimer_sejour, methods=["GET"])

        # API SÉJOURS (sans rechargement avec fetch)
        self.app.add_url_rule("/api/enregistrer_sejour", view_func=self.cp.api_enregistrer_sejour, methods=["POST"])
        self.app.add_url_rule("/api/get_sejours", view_func=self.cp.api_get_sejours, methods=["GET"])
        self.app.add_url_rule("/api/supprimer_sejour/<int:id_sejour>", view_func=self.cp.api_supprimer_sejour, methods=["DELETE"])

        # Publication MQTT logements
        self.app.add_url_rule("/publier_logements", endpoint="publier_logements", view_func=self.cp.publier_logements, methods=["POST"])

        # Actions messages (rechargement classique)
        self.app.add_url_rule("/enregistrer_message", view_func=self.cp.enregistrer_message, methods=["POST"])
        self.app.add_url_rule("/supprimer_message/<int:id_message>", view_func=self.cp.supprimer_message, methods=["GET"])

        # API MESSAGES (sans rechargement avec fetch) - optionnel
        # self.app.add_url_rule("/api/enregistrer_message", view_func=self.cp.api_enregistrer_message, methods=["POST"])
        # self.app.add_url_rule("/api/get_messages", view_func=self.cp.api_get_messages, methods=["GET"])
        # self.app.add_url_rule("/api/supprimer_message/<int:id_message>", view_func=self.cp.api_supprimer_message, methods=["DELETE"])

    def run(self):
        """Lance l'application Flask."""
        self.app.run()