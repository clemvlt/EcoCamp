import paho.mqtt.client as mqtt

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="cleaner"
)
client.connect("172.16.4.31", 1883, 60)
client.loop_start()

macs = ["88:a2:9e:9a:25:63", "88:a2:9e:9a:25:65"]
vieux_noms = ["mobil-home__01", "mobil-home__03"]

suffixes = [
    "",           # nom_hebergement lui-même
    "/donnees",
    "/quota",
    # ajoute ici les autres sous-topics si besoin
]

for mac in macs:
    for nom in vieux_noms:
        for suffix in suffixes:
            topic = f"ecocamp/tableau_bord/{mac}/nom_hebergement/{nom}{suffix}"
            client.publish(topic, payload="", qos=1, retain=True)
            print(f"Nettoyé : {topic}")

client.loop_stop()
client.disconnect()