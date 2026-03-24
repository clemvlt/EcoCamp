#!/usr/bin/env python3
"""
Test de la classe Database
"""

import pymysql
from test_config import Config


class Database:

    def __init__(self, config):
        self.config = config
        self.connexion = None

    def connecter(self):
        try:
            self.connexion = pymysql.connect(**self.config, autocommit=True)
            print(f"Connecté BDD ({self.config['host']})")
            return True
        except:
            return False

    def sauvegarder_consommation(self, valeur):
        if not self.connexion and not self.connecter():
            print("Erreur: Impossible de se connecter à la BDD")
            return False

        requete = """
        INSERT IGNORE INTO consommation
        (index_consommation, id_hebergement, id_type_flux)
        VALUES (%s, 10, 3)
        """

        try:
            curseur = self.connexion.cursor()
            curseur.execute(requete, (valeur,))
            curseur.close()
            print(f"Sauvegardé en BDD: {valeur} Wh")
            return True
        except Exception as e:
            print(f"Erreur sauvegarde BDD: {e}")
            return False

    def tester_connexion(self):
        try:
            if self.connecter():
                curseur = self.connexion.cursor()
                curseur.execute("SELECT 1")
                curseur.close()
                return True
        except Exception as e:
            print(f"Erreur test BDD: {e}")
            return False


def main():
    """Test de la classe Database"""
    print("=== Test de la classe Database ===")
    
    # Chargement de la configuration
    config_manager = Config()
    config_data = config_manager.charger_config()
    
    if not config_data:
        print("Impossible de charger la configuration")
        return
    
    # Test de connexion
    db = Database(config_data["db"])
    
    print("\nTest de connexion à la BDD...")
    if db.tester_connexion():
        print("Connexion BDD réussie")
        print("\nLa base de données est prête à recevoir les vraies valeurs du capteur")
        print("\nTest Database terminé")
    else:
        print("Connexion BDD échouée")


if __name__ == "__main__":
    main()
