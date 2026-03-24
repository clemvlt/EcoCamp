#!/usr/bin/env python3
"""
Test de la classe ReceptionData
"""

from test_database import Database
from test_config import Config


class ReceptionData:

    def __init__(self, database, id_hebergement):
        self.database = database
        self.id_hebergement = id_hebergement

    def traiter_donnees(self, topic, payload):
        try:
            valeur = float(payload)
            if self.database.sauvegarder_consommation(valeur):
                # Plus d'affichage ici pour éviter la répétition
                pass
        except:
            pass


def main():
    """Test de la classe ReceptionData"""
    print("=== Test de la classe ReceptionData ===")
    
    # Initialisation
    config_manager = Config()
    config_data = config_manager.charger_config()
    
    if not config_data:
        print("Impossible de charger la configuration")
        return
    
    db = Database(config_data["db"])
    reception = ReceptionData(db, 10)
    
    # Test avec MQTT réel pour obtenir les vraies valeurs du capteur
    print("\nTest de traitement des données MQTT en temps réel...")
    print("Écoute des vraies valeurs du capteur Shelly...")
    
    # Import du client MQTT pour écoute réelle
    from test_mqtt import MqttReceptionElec
    
    # Création du client MQTT avec callback vers ReceptionData
    mqtt_client = MqttReceptionElec(
        config_data["mqtt"]["broker"],
        config_data["mqtt"]["port"],
        config_data["mqtt"]["topics"],
        reception.traiter_donnees
    )
    
    print("\nDémarrage de l'écoute MQTT (15 secondes)...")
    print("En attente des vraies valeurs du capteur...")
    
    import time
    if mqtt_client.connecter():
        # Écoute pendant 15 secondes pour capturer les vraies valeurs
        time.sleep(15)
        mqtt_client.deconnecter()
        print("\nTest ReceptionData terminé")
    else:
        print("Échec de la connexion MQTT")


if __name__ == "__main__":
    main()
