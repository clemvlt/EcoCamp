document.addEventListener('DOMContentLoaded', function() {
    if (typeof rawData === 'undefined' || rawData.length === 0) return;

    // --- FORCE L'ÉCHANGE SELON LA VALEUR RÉELLE ---
    // On ignore le texte "Eau/Elec" de la base car les IDs sont inversés.
    // Dans tes données : l'Elec est à ~26 000 et l'Eau à ~125.
    
    // On met les grosses valeurs dans l'Électricité
    const datasetElec = rawData.filter(d => d.valeur > 1000).reverse();
    
    // On met les petites valeurs dans l'Eau
    const datasetEau = rawData.filter(d => d.valeur <= 1000).reverse();

    // --- MISE À JOUR DES CARTES ---
    if (datasetEau.length > 0) {
        document.getElementById('valeurEau').textContent = datasetEau[datasetEau.length - 1].valeur + " L";
    }
    if (datasetElec.length > 0) {
        document.getElementById('valeurElec').textContent = datasetElec[datasetElec.length - 1].valeur + " kWh";
    }

    // --- CONFIGURATION DU GRAPHIQUE ---
    const ctx = document.getElementById('consoChart').getContext('2d');
    const labels = datasetElec.map(d => d.label.split(' (')[0]); 

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Consommation Eau (L)',
                    data: datasetEau.map(d => d.valeur),
                    backgroundColor: 'rgba(0, 90, 150, 0.7)',
                    yAxisID: 'yEau', 
                },
                {
                    label: 'Index Électricité (kWh)',
                    data: datasetElec.map(d => d.valeur),
                    backgroundColor: 'rgba(251, 192, 45, 0.7)',
                    yAxisID: 'yElec',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                yEau: { position: 'left', title: { display: true, text: 'Eau (L)' } },
                yElec: { position: 'right', title: { display: true, text: 'Élec (kWh)' }, grid: { drawOnChartArea: false } }
            }
        }
    });
});