from flask import Flask
from controleur import ControleurPrincipal
from flask_mysqldb import MySQL


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
		self.app.add_url_rule("/",view_func=self.cp.afficher_login,methods=["GET"])
		self.app.add_url_rule("/test_login",view_func=self.cp.traiter_login,methods=["POST"])
		self.app.add_url_rule("/index", endpoint="index", view_func=self.cp.afficher_index, methods=["GET"])
		self.app.add_url_rule("/sejours", endpoint="sejours", view_func=self.cp.afficher_sejours, methods=["GET"])

		

	def run(self):
		"""
		Lancement de l'application
		"""
		self.app.run()

	 
