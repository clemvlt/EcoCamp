document.addEventListener("DOMContentLoaded", function () {
    const boutonConnexion = document.getElementById("formulaire_login");
    const form = document.querySelector("form");
    const togglePassword = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("password");
    const eyeIcon = document.getElementById("eyeIcon");

    // Connexion via bouton ou touche Entrée
    boutonConnexion.addEventListener("click", test_login);
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        test_login();
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
    fetch("/test_login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            identifiant: document.getElementById("login").value,
            pwd: document.getElementById("password").value
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