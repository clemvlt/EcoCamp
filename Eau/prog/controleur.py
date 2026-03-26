import json
from bdd import DatabaseManager

class Controleur:
    
    def __init__(self, config):
        self.config = config
        self.db_manager = DatabaseManager(config["database"])
        self.id_hebergement = 7  # Valeur par défaut
        self.id_type_flux = 4    # Valeur fixe
    
    def set_hebergement(self, id_hebergement):
        """Définir l'ID d'hébergement"""
        self.id_hebergement = id_hebergement
        print(f"ID hébergement défini sur : {id_hebergement}")
    
    def sauvegarder(self, index, id_hebergement=None):
        """Sauvegarder les données avec les paramètres fournis ou ceux par défaut"""
        hebergement_id = id_hebergement if id_hebergement is not None else self.id_hebergement
        
        return self.db_manager.sauvegarder_consommation(index, hebergement_id, self.id_type_flux)
    
    def process(self, payload):
        """Traiter les données reçues et les sauvegarder"""
        try:
            data = json.loads(payload.decode())
            print("JSON reçu OK")
            
            # Extraction du compteur
            counter_values = data["uplink_message"]["decoded_payload"]["bytes"]["counterValues"]
            index = float(counter_values[0])  # Channel A
            print("Index extrait :", index)
            
            # Sauvegarder avec les paramètres actuels
            success = self.sauvegarder(index)
            
            if success:
                print(f"Données traitées et sauvegardées avec succès")
            else:
                print("Échec de la sauvegarde des données")
                
        except Exception as e:
            print(f"Erreur traitement : {e}")
    
    def get_status(self):
        """Obtenir le statut du contrôleur et de la base de données"""
        db_status = self.db_manager.test_connection()
        return {
            "database_connected": db_status,
            "id_hebergement": self.id_hebergement,
            "id_type_flux": self.id_type_flux
        }
    
    def close(self):
        """Fermer les connexions"""
        self.db_manager.close()


if __name__ == "__main__":
    # Test du contrôleur avec la nouvelle architecture
    import json
    with open('config2.json', 'r') as f:
        config = json.load(f)
    
    # Création du contrôleur
    controleur = Controleur(config)
    
    # Affichage du statut
    status = controleur.get_status()
    print(f"Statut du contrôleur : {status}")
    
    # Test de traitement sans insertion (simulation)
    print("Test de traitement des données (sans insertion en base)...")
    test_payload = b'{"uplink_message":{"decoded_payload":{"bytes":{"counterValues":[123.45]}}}}'
    
    # Simuler le traitement sans sauvegarder
    try:
        data = json.loads(test_payload.decode())
        print("JSON reçu OK")
        counter_values = data["uplink_message"]["decoded_payload"]["bytes"]["counterValues"]
        index = float(counter_values[0])
        print(f"Index extrait : {index}")
        print("Traitement simulé terminé avec succès")
    except Exception as e:
        print(f"Erreur traitement : {e}")
    
    # Test avec différents paramètres (sans insertion)
    controleur.set_hebergement(8)
    print(f"ID hébergement changé pour : {controleur.id_hebergement}")
    
    # Fermeture
    controleur.close()
    print("Test du contrôleur terminé - aucune donnée insérée en base")