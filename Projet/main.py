from controleur import Controleur
from reception_eau import ReceptionDataEau
import time

config = {
    "db": {
        "host": "172.16.4.102",
        "user": "ecocamp",
        "password": "ecocamp2026",
        "db_name": "ecocamp",
        "port": "3006"
    },
    "mqtt": {
        "broker": "eu1.cloud.thethings.network",
        "port": 1883,
        "topic": "v3/projet-ecocamp-mq@ttn/devices/eau-ecocamp-mq/up",
        "user": "projet-ecocamp-mq@ttn",
        "password": "NNSXS.V6WQTOUTPR74JB44OUDCXONXATPM6Z4TNZBZCQY.CMVWCYEZKHSL2NMDVAHHYMQOOW7XYVORXR3TEWMY6T5U5XZJPAAQ"
    }
}

controleur = Controleur(config["db"])

# On passe le controleur comme handler
mqtt = ReceptionDataEau(config, controleur)

# Pour garder le script actif
import time
while True:
    time.sleep(1)