import logging
from flask import Flask
from controleur import ControleurPrincipal
from flask_mysqldb import MySQL
from datetime import timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s : %(message)s'
)

class Application:
    """
    Instancie Flask, MySQL et ControleurPrincipal.
    Crée les routes et lance l'application.
    """
    def __init__(self):
        template_dir = "../templates"
        static_dir = "../static"

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

        self.cp = ControleurPrincipal(self)
        self.__routage()

    def __routage(self):
        """Enregistrement de toutes les routes de l'application."""
        self.app.before_request(self.cp.test_before_request)
        #Erreur 404
        
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

        # Actions séjours
        self.app.add_url_rule("/enregistrer_sejour", view_func=self.cp.enregistrer_sejour, methods=["POST"])
        self.app.add_url_rule("/supprimer_sejour/<int:id_sejour>", view_func=self.cp.supprimer_sejour, methods=["GET"])

        # Actions messages
        self.app.add_url_rule("/enregistrer_message", view_func=self.cp.enregistrer_message, methods=["POST"])
        self.app.add_url_rule("/supprimer_message/<int:id_message>", view_func=self.cp.supprimer_message, methods=["GET"])

    def run(self):
        """Lance l'application Flask."""
        self.app.run()