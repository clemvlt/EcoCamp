#!/usr/bin/env python3
"""
Test de la classe Controleur
"""

import time
from test_config import Config
from test_database import Database
from test_reception_data import ReceptionData
from test_mqtt import MqttReceptionElec


class Controleur:

    def __init__(self):
        self.config = Config()
        self.donnees_config = self.config.charger_config()
        
        if not self.donnees_config:
            return
        
        self.bdd = Database(self.donnees_config["db"])
        self.reception_data = ReceptionData(self.bdd, 10)
        
        self.mqtt = MqttReceptionElec(
            self.donnees_config["mqtt"]["broker"],
            self.donnees_config["mqtt"]["port"],
            self.donnees_config["mqtt"]["topics"],
            self.reception_data.traiter_donnees
        )

    def tester_connexions(self):
        bdd_ok = self.bdd.tester_connexion()
        mqtt_ok = self.mqtt.tester_connexion()
        return bdd_ok and mqtt_ok

    def demarrer(self):
        if not self.tester_connexions():
            print("Erreur de connexion")
            return
        
        try:
            if self.mqtt.connecter():
                self.mqtt.demarrer_ecoute()
        except KeyboardInterrupt:
            self.mqtt.deconnecter()
        except:
            self.mqtt.deconnecter()


def main():
    """Test de la classe Controleur"""
    print("=== Test de la classe Controleur ===")
    
    # Initialisation du contrôleur
    controleur = Controleur()
    
    if not controleur.donnees_config:
        print("Impossible de charger la configuration")
        return
    
    print("\nTest des connexions...")
    if controleur.tester_connexions():
        print("Toutes les connexions sont OK")
        
        print("\nDemarrage du contrôleur (10 secondes)...")
        print("   Le contrôleur va coordonner MQTT et BDD...")
        
        if controleur.mqtt.connecter():
            # Test pendant 10 secondes
            time.sleep(10)
            controleur.mqtt.deconnecter()
            print("\nTest contrôleur terminé")
        else:
            print("Échec du démarrage MQTT")
    else:
        print("Une ou plusieurs connexions ont échoué")
    
    print("\nTest Controleur terminé")


if __name__ == "__main__":
    main()
