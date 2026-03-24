#!/usr/bin/env python3
"""
Test de la classe Config
"""

from config_simple import get_config


class Config:

    def __init__(self):
        self.config_dir = "config"

    def charger_config(self):
        try:
            # Utilisation de la configuration simple sans chiffrement
            config_data = get_config()
            return config_data
            
        except:
            print("Erreur configuration")
            return None


def main():
    """Test de la classe Config"""
    print("=== Test de la classe Config ===")
    
    config = Config()
    donnees = config.charger_config()
    
    if donnees:
        print("Configuration chargée avec succès")
        print(f"Broker MQTT: {donnees['mqtt']['broker']}")
        print(f"Port MQTT: {donnees['mqtt']['port']}")
        print(f"Topics: {donnees['mqtt']['topics']}")
        print(f"BDD Host: {donnees['db']['host']}")
        print(f"BDD User: {donnees['db']['user']}")
        print(f"ID hebergement: {donnees['id_hebergement']}")
    else:
        print("Échec du chargement de la configuration")


if __name__ == "__main__":
    main()

