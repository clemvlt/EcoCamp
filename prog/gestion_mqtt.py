import paho.mqtt.client as mqttclient
import json

class GestionMQTT:
    
    def __init__(self, mqtt_config, handler):
        self.mqtt_config = mqtt_config
        self.handler = handler
        self.client_mqtt = None
        self.connect()
    
    def connect(self):
        """Établir la connexion MQTT"""
        try:
            self.client_mqtt = mqttclient.Client(
                callback_api_version=mqttclient.CallbackAPIVersion.VERSION2,
                clean_session=True
            )
            
            self.client_mqtt.on_connect = self.on_connect
            self.client_mqtt.on_disconnect = self.on_disconnect
            self.client_mqtt.on_message = self.on_message
            
            self.client_mqtt.username_pw_set(
                self.mqtt_config['user'],
                password=self.mqtt_config['password']
            )
            
            self.client_mqtt.connect_async(
                self.mqtt_config['broker'],
                self.mqtt_config['port']
            )
            
            self.client_mqtt.loop_start()
            print("Client MQTT initialisé")
            
        except Exception as e:
            print(f"Erreur de connexion MQTT : {e}")
            self.client_mqtt = None
    
    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        """Callback de connexion MQTT"""
        print("***Connexion MQTT***")
        
        if reason_code == 0:
            topic = self.mqtt_config['topic']
            self.client_mqtt.subscribe([(topic, 2)])
            print(f"Abonné au topic : {topic}")
        else:
            print(f"Erreur de connexion MQTT : {reason_code}")
    
    def on_disconnect(self, client, userdata, reason_code, properties=None):
        """Callback de déconnexion MQTT"""
        print(f"***Déconnexion MQTT*** : {reason_code}")
    
    def on_message(self, client, userdata, msg):
        """Callback de réception de message MQTT"""
        print("***Message MQTT reçu***")
        
        try:
            # Transférer le payload au handler
            self.handler.process(msg.payload)
            
        except Exception as e:
            print(f"Erreur traitement message MQTT : {e}")
    
    def is_connected(self):
        """Vérifier si le client MQTT est connecté"""
        if self.client_mqtt:
            return self.client_mqtt.is_connected()
        return False
    
    def reconnect(self):
        """Reconnecter le client MQTT"""
        if self.client_mqtt:
            self.client_mqtt.disconnect()
        self.connect()
    
    def stop(self):
        """Arrêter le client MQTT"""
        if self.client_mqtt:
            self.client_mqtt.loop_stop()
            self.client_mqtt.disconnect()
            print("Client MQTT arrêté")


if __name__ == "__main__":
    # Test du gestionnaire MQTT
    with open('config2.json', 'r') as f:
        config = json.load(f)
    
    # Handler mock pour tester
    class MockHandler:
        def process(self, payload):
            print(f"Mock handler reçu payload: {payload.decode()}")
    
    # Test du gestionnaire MQTT
    mock_handler = MockHandler()
    mqtt_manager = GestionMQTT(config["mqtt"], mock_handler)
    
    print("Gestionnaire MQTT démarré. En attente de messages...")
    print("Appuyez Ctrl+C pour arrêter")
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nArrêt du gestionnaire MQTT...")
        mqtt_manager.stop()
        print("Gestionnaire MQTT arrêté")
