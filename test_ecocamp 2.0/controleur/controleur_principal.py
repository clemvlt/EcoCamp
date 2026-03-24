# Dans controleur_principal.py
from flask import render_template, request, redirect, url_for # Ajoutez redirect et url_for
from modele.Client import Client 

class ControleurPrincipal:
    def __init__(self, appli):
        self.mysql = appli.mysql

    def afficher_login(self):
        return render_template("login.html")

    
    def afficher_index(self):
        return render_template("index.html")
    

    def traiter_login(self):
        login = request.form["login"]
        mdp = request.form["password"]

        client = Client(self.mysql)
        nb_utilisateurs = client.test_login(login, mdp)

        if nb_utilisateurs > 0:
            # SI OK : Redirection vers la route 'index'
            return redirect(url_for('index'))
        else:
            # SI PAS OK : Retour au login avec un message
            return redirect('/')
        

    def afficher_sejours(self):
        return render_template("sejours.html")