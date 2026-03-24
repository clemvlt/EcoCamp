document.addEventListener("DOMContentLoaded", _ => {
    const bouton_connexion = document.getElementById("formulaire_login")

    bouton_connexion.addEventListener("click",test_login)

})


function test_login(){
    fetch("/test_login",{
        method :"post",
        headers: {
            "Content-Type": "application/json"
        }, 
        body: JSON.stringify({
            identifiant: document.getElementById ("login").value,
            pwd: document.getElementById ("password").value
        })
    })
    .then(response => response.json())

    .then(
        data => traiter_resultat_login(data["valeur"])
    )   
    .catch(error => console.error("Erreur : ",error))
}


function traiter_resultat_login(resu){
    if(resu == 1){
        location.href="/index"
    }
    else{
        data = document.getElementById("message_erreur");
        data.textContent = "Nom d'utilisateur ou mot de passe invalide";
        document.getElementById ("password").value = ""
        document.getElementById ("password").focus();
    }
}


document.addEventListener("DOMContentLoaded", _ => {
    const bouton_connexion = document.getElementById("formulaire_login")
    const form = document.querySelector("form")

    bouton_connexion.addEventListener("click", test_login)

    // Gestion de la touche Entrée
    form.addEventListener("submit", function(e) {
        e.preventDefault(); // empêche le submit classique
        test_login();
    })
})



document.addEventListener("DOMContentLoaded", function() {
    // Gestionnaire pour le bouton de connexion
    const bouton_connexion = document.getElementById("formulaire_login");
    const form = document.querySelector("form");

    bouton_connexion.addEventListener("click", test_login);

    // Gestion de la touche Entrée
    form.addEventListener("submit", function(e) {
        e.preventDefault(); // empêche le submit classique
        test_login();
    });

    // Gestionnaire pour l'œil du mot de passe
    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('password');
    const eyeIcon = document.getElementById('eyeIcon');

    if (togglePassword && password && eyeIcon) {
        togglePassword.addEventListener('click', function() {
            // Basculer le type de l'input
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            
            // Changer l'icône
            if (type === 'password') {
                eyeIcon.classList.remove('fa-eye-slash');
                eyeIcon.classList.add('fa-eye');
            } else {
                eyeIcon.classList.remove('fa-eye');
                eyeIcon.classList.add('fa-eye-slash');
            }
        });
    }
});

function test_login() {
    fetch("/test_login", {
        method: "post",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            identifiant: document.getElementById("login").value,
            pwd: document.getElementById("password").value
        })
    })
    .then(response => response.json())
    .then(data => traiter_resultat_login(data["valeur"]))
    .catch(error => console.error("Erreur : ", error));
}

