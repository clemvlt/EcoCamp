#!/usr/bin/env python3
"""
EcoCamp - Monitoring consommation électrique
Version modulaire avec imports depuis fichiers de test
"""

# Import de la classe App depuis son fichier
from test_app import App


def main():
    """Point d'entrée principal"""
    try:
        app = App()
        app.run()
    except:
        pass


if __name__ == "__main__":
    main()
