import paho.mqtt.client as mqttclient


class ReceptionDataEau:

    def __init__(self, config, handler):
        self.config = config
        self.handler = handler
        self.init_mqtt()

    def init_mqtt(self):
        try:
            self.client_mqtt = mqttclient.Client("", clean_session=True)

            self.client_mqtt.on_connect = self.onConnectMQTT
            self.client_mqtt.on_disconnect = self.onDisConnectMQTT

            self.client_mqtt.username_pw_set(
                self.config['mqtt']['user'],
                password=self.config['mqtt']['password']
            )

            self.client_mqtt.connect_async(
                self.config['mqtt']['broker'],
                self.config['mqtt']['port']
            )

            self.client_mqtt.loop_start()

        except Exception as e:
            print("Erreur Connect MQTT :", e)

    def onConnectMQTT(self, client, userdata, flags, rc, properties=None):
        print("***Connexion MQTT***")

        if rc == 0:
            topic = self.config['mqtt']['topic']

            self.client_mqtt.subscribe([(topic, 2)])
            self.client_mqtt.on_message = self.onMessageMQTT
        else:
            print("Erreur connexion :", rc)

    def onDisConnectMQTT(self, client, userdata, rc):
        print("***DECO MQTT***", rc)

    def onMessageMQTT(self, client, userdata, msg):
        print("***MQTT MESSAGE***")

        try:
            # Envoie direct au controleur
            self.handler.process(msg.payload)

        except Exception as e:
            print("Erreur MESSAGE MQTT :", e)