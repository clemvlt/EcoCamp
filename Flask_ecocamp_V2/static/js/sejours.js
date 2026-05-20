// Attendre que le DOM soit chargé
document.addEventListener("DOMContentLoaded", function() {
    // Gestion du formulaire nouveau séjour avec fetch
    const formSejour = document.getElementById("formNouveauSejour");
    if (formSejour) {
        formSejour.addEventListener("submit", async function(e) {
            e.preventDefault();
            
            const id_hebergement = document.getElementById("id_hebergement").value;
            const date_debut = document.getElementById("date_debut").value;
            const date_fin = document.getElementById("date_fin").value;
            
            // Validation des dates
            if (!id_hebergement || !date_debut || !date_fin) {
                toast.error("Veuillez remplir tous les champs");
                return;
            }
            
            if (new Date(date_debut) > new Date(date_fin)) {
                toast.error("La date de début doit être antérieure à la date de fin");
                return;
            }
            
            try {
                const response = await fetch("/api/enregistrer_sejour", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        id_hebergement: id_hebergement,
                        date_debut: date_debut,
                        date_fin: date_fin
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    toast.success("✅ Séjour créé avec succès !");
                    await rechargerListeSejours();
                    setTimeout(() => {
                        fermerModale();
                        formSejour.reset();
                    }, 1000);
                } else {
                    toast.error("❌ " + (data.message || "Erreur lors de la création"));
                }
            } catch (error) {
                console.error("Erreur:", error);
                toast.error("❌ Erreur lors de la création du séjour");
            }
        });
    }
});

function ouvrirModale() { 
    document.getElementById("fenetreSejour").style.display = "block"; 
}

function fermerModale() { 
    document.getElementById("fenetreSejour").style.display = "none"; 
}

// Recharger la liste des séjours
async function rechargerListeSejours() {
    try {
        const response = await fetch("/api/get_sejours");
        const sejours = await response.json();
        
        const tbody = document.getElementById("sejoursTableBody");
        if (tbody) {
            if (sejours.length === 0) {
                tbody.innerHTML = `<tr id="empty-row"><td colspan="6" class="empty-table-cell">Aucun séjour enregistré.</td>`;
            } else {
                tbody.innerHTML = sejours.map(s => `
                    <tr id="sejour-${s.id_sejour}">
                        <td>#${s.id_sejour}</td>
                        <td><strong>${escapeHtml(s.nom_hebergement)}</strong></td>
                        <td>${s.date_debut_sejour}</td>
                        <td>${s.date_fin_sejour}</td>
                        <td><span class="status-badge success">Confirmé</span></td>
                        <td style="text-align: center;">
                            <button type="button" class="btn-delete" onclick="supprimerSejour(${s.id_sejour}, '${escapeHtml(s.nom_hebergement)}')">
                                🗑️
                            </button>
                        </td>
                    </tr>
                `).join('');
            }
        }
    } catch (error) {
        console.error("Erreur lors du rechargement:", error);
        toast.error("Erreur lors du chargement des séjours");
    }
}

// Suppression avec fetch
async function supprimerSejour(idSejour, nomHebergement) {
    if (confirm(`Supprimer le séjour pour ${nomHebergement} ?`)) {
        try {
            const response = await fetch(`/api/supprimer_sejour/${idSejour}`, {
                method: "DELETE",
                headers: { "Content-Type": "application/json" }
            });
            
            const data = await response.json();
            
            if (data.success) {
                toast.success("✅ Séjour supprimé avec succès !");
                await rechargerListeSejours();
            } else {
                toast.error("❌ " + (data.message || "Erreur lors de la suppression"));
            }
        } catch (error) {
            console.error("Erreur:", error);
            toast.error("❌ Erreur lors de la suppression");
        }
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Fermer les modales en cliquant à l'extérieur
window.onclick = function(event) {
    if (event.target.className === "modal") {
        event.target.style.display = "none";
    }
}