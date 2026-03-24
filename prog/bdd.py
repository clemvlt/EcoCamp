import pymysql
import json

class DatabaseManager:
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.db = None
        self.connect()
    
    def connect(self):
        """Établir la connexion à la base de données"""
        try:
            self.db = pymysql.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['db_name'],
                autocommit=True
            )
            print("Connexion à la base de données établie")
        except Exception as e:
            print(f"Erreur de connexion à la base de données : {e}")
            self.db = None
    
    def reconnect(self):
        """Reconnecter à la base de données"""
        if self.db:
            self.db.close()
        self.connect()
    
    def sauvegarder_consommation(self, index, id_hebergement, id_type_flux):
        """Sauvegarder les données de consommation dans la base de données"""
        if not self.db:
            print("Pas de connexion à la base de données")
            return False
            
        try:
            with self.db.cursor() as cursor:
                sql = """
                INSERT INTO consommation
                (index_consommation, id_hebergement, id_type_flux)
                VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (index, id_hebergement, id_type_flux))
                self.db.commit()
                print(f"Index {index} enregistré (flux {id_type_flux}, hébergement {id_hebergement})")
                return True
                
        except Exception as e:
            print(f"Erreur SQL lors de la sauvegarde : {e}")
            # Tenter de reconnecter en cas d'erreur de connexion
            if "MySQL server has gone away" in str(e) or "Connection" in str(e):
                print("Tentative de reconnexion...")
                self.reconnect()
                return self.sauvegarder_consommation(index, id_hebergement, id_type_flux)
            return False
    
    def test_connection(self):
        """Tester la connexion à la base de données"""
        if not self.db:
            return False
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            print(f"Erreur de test de connexion : {e}")
            return False
    
    def close(self):
        """Fermer la connexion à la base de données"""
        if self.db:
            self.db.close()
            print("Connexion à la base de données fermée")


if __name__ == "__main__":
    # Test du gestionnaire de base de données
    import json
    with open('config2.json', 'r') as f:
        config = json.load(f)
    
    # Test de la base de données
    db_manager = DatabaseManager(config["database"])
    
    # Test de connexion uniquement
    if db_manager.test_connection():
        print("Test de connexion réussi")
        print("La base de données est prête à recevoir les données du capteur")
    else:
        print("Échec du test de connexion")
    
    db_manager.close()
    print("Test du gestionnaire de base de données terminé")
