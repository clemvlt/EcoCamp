import json
from gestion_mqtt import GestionMQTT

class ReceptionDataEau:
    
    def __init__(self, config, handler):
        self.config = config
        self.handler = handler
        self.mqtt_manager = GestionMQTT(config["mqtt"], self)
        self.messages_recus = 0
    
    def process(self, payload):
        """Traiter les données reçues et les transférer au handler principal"""
        try:
            print(f"Données eau reçues - Message #{self.messages_recus + 1}")
            
            # Transférer au handler principal (controleur)
            self.handler.process(payload)
            
            self.messages_recus += 1
            print(f"Message #{self.messages_recus} traité avec succès")
            
        except Exception as e:
            print(f"Erreur traitement données eau : {e}")
    
    def get_status(self):
        """Obtenir le statut du récepteur et MQTT"""
        return {
            "mqtt_connected": self.mqtt_manager.is_connected(),
            "messages_recus": self.messages_recus
        }
    
    def stop(self):
        """Arrêter le récepteur"""
        self.mqtt_manager.stop()


if __name__ == "__main__":
    # Test du récepteur de données eau
    with open('config2.json', 'r') as f:
        config = json.load(f)
    
    # Handler mock pour tester
    class MockHandler:
        def process(self, payload):
            print(f"Mock handler reçu payload: {payload}")
    
    # Test du récepteur
    mock_handler = MockHandler()
    recepteur = ReceptionDataEau(config, mock_handler)
    
    print("Récepteur de données eau démarré. En attente de messages...")
    
    try:
        import time
        while True:
            time.sleep(5)  # Afficher le statut toutes les 5 secondes
            status = recepteur.get_status()
            print(f"Statut : {status}")
            
    except KeyboardInterrupt:
        print("\nArrêt du récepteur...")
        recepteur.stop()
        print("Récepteur arrêté")