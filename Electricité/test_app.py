#!/usr/bin/env python3
"""
Test de la classe App
"""

from test_controleur import Controleur


class App:

    def __init__(self):
        self.controleur = Controleur()

    def run(self):
        self.controleur.demarrer()


def main():
    """Test de la classe App"""
    print("=== Test de la classe App ===")
    print("L'application complète avec toutes les classes")
    
    app = App()
    app.run()


if __name__ == "__main__":
    main()
