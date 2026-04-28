from application import Application

# Créez l'instance comme dans index.py
monApp = Application()

# L'application Flask est dans l'attribut 'app'
# C'est cet objet que Gunicorn doit utiliser
application = monApp.app

if __name__ == "__main__":
    application.run()
