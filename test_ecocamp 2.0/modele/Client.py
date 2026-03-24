from controleur import *


class Client:
	def __init__(self,mysql):
		self.mysql = mysql
		

	def test_login(self,login,mdp):
		conn = self.mysql.connect
		cursor = conn.cursor()
		
		requete = "SELECT count(*) as valeur FROM administrateur WHERE login_administrateur = %s AND mdp_administrateur = %s"
		parametres = (login, mdp)
		cursor.execute(requete,parametres)

		res = cursor.fetchone()
		cursor.close()
        
		return  res["valeur"]
			
			