from flask import Flask
from controleur import ControleurPrincipal
from flask_mysqldb import MySQL
from datetime import timedelta

class Application:
	"""
	Instancie Flask,MySQL et ControleurPrincipal
	
	Crée les routes et lance l'application
	"""
	def __init__(self):

        #Initialisation des chemins
		template_dir = "../templates"
		static_dir = "../static"
		
		#Instanciation de Flask
		self.app = Flask(__name__,template_folder = template_dir,static_folder = static_dir,instance_relative_config = True)
		self.app.config.from_pyfile("config.cfg")
		self.app.permanent_session_lifetime = timedelta(
			seconds=self.app.config['PERMANT_SESSION_LIFETIME']
		)

		#Instanciation de MySQL
		self.mysql = MySQL()
		self.mysql.init_app(self.app)

		#Intanciation de ControleurPrincipal
		self.cp = ControleurPrincipal(self)
		
		self.__routage()


	def __routage(self):
		"""
		Réalisation du routage
		"""
		self.app.before_request(self.cp.test_before_request) # Test si session
		self.app.add_url_rule("/",view_func=self.cp.afficher_login,methods=["GET"]) # renvoie vers la page de base 
		self.app.add_url_rule("/test_login",view_func=self.cp.traiter_login,methods=["POST"]) #Traitement  des infos du formulaire

		self.app.add_url_rule("/index", endpoint="index", view_func=self.cp.afficher_index, methods=["GET"])
		self.app.add_url_rule("/sejours", endpoint="sejours", view_func=self.cp.afficher_sejours, methods=["GET"]) 
		self.app.add_url_rule("/quotas", endpoint="quotas", view_func=self.cp.afficher_quotas, methods=["GET", "POST"])
		self.app.add_url_rule("/consommations", endpoint="consommations", view_func=self.cp.afficher_consommations, methods=["GET"])
		self.app.add_url_rule("/messages", endpoint="messages", view_func=self.cp.afficher_messages, methods=["GET"])
		self.app.add_url_rule("/deconnexion", view_func=self.cp.deconnexion, methods=["GET"]) # Route pour la déconnexion 
		self.app.add_url_rule("/enregistrer_sejour", view_func=self.cp.enregistrer_sejour, methods=["POST"])
		self.app.add_url_rule("/supprimer_sejour/<int:id_sejour>", view_func=self.cp.supprimer_sejour)
		self.app.add_url_rule("/sejours", view_func=self.cp.afficher_sejours)
		

		

	def run(self):
		"""
		Lancement de l'application
		"""
		self.app.run()

	 
