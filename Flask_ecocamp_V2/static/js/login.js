document.addEventListener("DOMContentLoaded", function () {
    const boutonConnexion = document.getElementById("formulaire_login");
    const loginInput = document.getElementById("login");
    const passwordInput = document.getElementById("password");
    const togglePassword = document.getElementById("togglePassword");
    const eyeIcon = document.getElementById("eyeIcon");

    // Connexion via bouton
    boutonConnexion.addEventListener("click", test_login);

    // Connexion via touche Entrée
    loginInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            test_login();
        }
    });
    
    passwordInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            test_login();
        }
    });

    // Afficher / masquer le mot de passe
    if (togglePassword && passwordInput && eyeIcon) {
        togglePassword.addEventListener("click", function () {
            const isPassword = passwordInput.getAttribute("type") === "password";
            passwordInput.setAttribute("type", isPassword ? "text" : "password");
            eyeIcon.classList.toggle("fa-eye", !isPassword);
            eyeIcon.classList.toggle("fa-eye-slash", isPassword);
        });
    }
});

function test_login() {
    const identifiant = document.getElementById("login").value;
    const pwd = document.getElementById("password").value;
    
    // Vérification que les champs ne sont pas vides
    if (!identifiant || !pwd) {
        const msgErreur = document.getElementById("message_erreur");
        msgErreur.textContent = "Veuillez remplir tous les champs";
        return;
    }
    
    fetch("/test_login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            identifiant: identifiant,
            pwd: pwd
        })
    })
    .then(response => response.json())
    .then(data => traiter_resultat_login(data["valeur"]))
    .catch(error => console.error("Erreur fetch login : ", error));
}

function traiter_resultat_login(resu) {
    if (resu == 1) {
        location.href = "/index";
    } else {
        const msgErreur = document.getElementById("message_erreur");
        msgErreur.textContent = "Nom d'utilisateur ou mot de passe invalide";
        document.getElementById("password").value = "";
        document.getElementById("password").focus();
    }
}