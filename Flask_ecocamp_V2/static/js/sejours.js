function ouvrirModale() { 
    document.getElementById("fenetreSejour").style.display = "block"; 
}

function fermerModale() { 
    document.getElementById("fenetreSejour").style.display = "none"; 
}

function ouvrirModaleSuppr(id, nom) {
    document.getElementById("nomHebergementSuppr").innerText = nom;
    document.getElementById("lienSupprimer").href = "/supprimer_sejour/" + id;
    document.getElementById("modalConfirmSuppr").style.display = "block";
}

function fermerModaleSuppr() { 
    document.getElementById("modalConfirmSuppr").style.display = "none"; 
}

window.onclick = function (event) {
    if (event.target.className === "modal") {
        event.target.style.display = "none";
    }
} 