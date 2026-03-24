from controleur import Controleur
from reception_eau import ReceptionDataEau
import json
import time

# Lire la configuration depuis le fichier JSON
with open('config2.json', 'r') as f:
    config = json.load(f)

# Créer le contrôleur avec la nouvelle architecture
controleur = Controleur(config)

# Afficher le statut initial
status = controleur.get_status()
print(f"Statut initial : {status}")

# Configurer les paramètres si nécessaire
controleur.set_hebergement(7)

# On passe le controleur comme handler pour le MQTT
mqtt = ReceptionDataEau(config, controleur)

if __name__ == "__main__":
    try:
        print("Application démarrée. En attente de messages MQTT...")
        print("Appuyez Ctrl+C pour arrêter")
        
        # Pour garder le script actif
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nArrêt de l'application...")
        mqtt.stop()
        controleur.close()
        print("Application arrêtée proprement")