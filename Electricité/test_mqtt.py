#!/usr/bin/env python3
"""
Test de la classe MqttReceptionElec
"""

import time
import warnings
import paho.mqtt.client as mqtt
from test_config import Config


class MqttReceptionElec:

    def __init__(self, broker, port, topics, callback=None):
        self.broker = broker
        self.port = port
        self.topics = topics
        self.callback = callback or self.callback_default
        self.client = None
        self.connecte = False
        self.deja_affiche = False
        self.topics_affiches = False

    def callback_default(self, topic, payload):
        """Callback par défaut si aucun callback n'est fourni"""
        print(f"Message MQTT - Topic: {topic}, Valeur: {payload}")

    def configurer_client(self):
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=UserWarning)
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connecte = True
            if not self.deja_affiche:
                print(f"Connecté MQTT ({self.broker})")
                self.deja_affiche = True
            self.abonne_topics()
        else:
            self.connecte = False

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            
            if self.callback:
                self.callback(topic, payload)
                
        except UnicodeDecodeError:
            # Gérer les messages qui ne sont pas du texte
            pass
        except Exception as e:
            # Gérer les autres erreurs MQTT
            pass

    def abonne_topics(self):
        if not self.topics_affiches:
            for topic in self.topics:
                result, mid = self.client.subscribe(topic)
                print(f"Topic: {topic}")
            self.topics_affiches = True

    def connecter(self):
        try:
            if not self.client:
                self.configurer_client()
            
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Erreur connexion MQTT: {e}")
            return False

    def deconnecter(self):
        if hasattr(self, 'client') and self.client and self.connecte:
            self.client.loop_stop()
            self.client.disconnect()
            self.connecte = False

    def demarrer_ecoute(self):
        if not self.client:
            self.configurer_client()
        
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            self.deconnecter()
        except Exception as e:
            # Gérer les erreurs MQTT y compris struct.error
            print(f"Erreur MQTT: {e}")
            self.deconnecter()

    def tester_connexion(self):
        try:
            test_client = mqtt.Client()
            test_client.connect(self.broker, self.port, 60)
            test_client.disconnect()
            return True
        except:
            return False


def callback_test(topic, payload):
    """Callback de test pour afficher les messages"""
    print(f" Message reçu - Topic: {topic}, Valeur: {payload}")


def main():
    """Test de la classe MqttReceptionElec"""
    print("=== Test de la classe MqttReceptionElec ===")
    
    # Configuration
    config_manager = Config()
    config_data = config_manager.charger_config()
    
    if not config_data:
        print("Impossible de charger la configuration")
        return
    
    # Test de connexion MQTT
    print("\nTest de connexion au broker MQTT...")
    mqtt_client = MqttReceptionElec(
        config_data["mqtt"]["broker"],
        config_data["mqtt"]["port"],
        config_data["mqtt"]["topics"],
        callback_test
    )
    
    if mqtt_client.tester_connexion():
        print("Test de connexion MQTT réussi")
        
        print("\nDémarrage de l'écoute MQTT (10 secondes)...")
        print("   Écoute des messages en temps réel...")
        
        if mqtt_client.connecter():
            # Écoute pendant 10 secondes
            time.sleep(10)
            mqtt_client.deconnecter()
            print("\nTest MQTT terminé")
        else:
            print("Échec de la connexion MQTT")
    else:
        print("Test de connexion MQTT échoué")
    
    print("\nTest MqttReceptionElec terminé")


if __name__ == "__main__":
    main()
