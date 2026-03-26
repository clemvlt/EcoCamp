document.addEventListener('DOMContentLoaded', function () {
    if (typeof rawData === 'undefined' || rawData.length === 0) return;

    // Filtrage par id_type_flux transmis depuis le template :
    //   id_type_flux == 4 → Eau
    //   id_type_flux == 3 → Électricité
    const datasetEau  = rawData.filter(d => d.id_type_flux === 4).reverse();
    const datasetElec = rawData.filter(d => d.id_type_flux === 3).reverse();

    // Mise à jour des cartes récapitulatives
    if (datasetEau.length > 0) {
        document.getElementById('valeurEau').textContent =
            datasetEau[datasetEau.length - 1].valeur + " L";
    }
    if (datasetElec.length > 0) {
        document.getElementById('valeurElec').textContent =
            datasetElec[datasetElec.length - 1].valeur + " kWh";
    }

    // Étiquettes de l'axe X (dates issues du dataset le plus fourni)
    const sourceLabels = datasetElec.length >= datasetEau.length ? datasetElec : datasetEau;
    const labels = sourceLabels.map(d => d.label.split(' (')[0]);

    const ctx = document.getElementById('consoChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Consommation Eau (L)',
                    data: datasetEau.map(d => d.valeur),
                    backgroundColor: 'rgba(0, 90, 150, 0.7)',
                    yAxisID: 'yEau'
                },
                {
                    label: 'Index Électricité (kWh)',
                    data: datasetElec.map(d => d.valeur),
                    backgroundColor: 'rgba(251, 192, 45, 0.7)',
                    yAxisID: 'yElec'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                yEau:  { position: 'left',  title: { display: true, text: 'Eau (L)' } },
                yElec: { position: 'right', title: { display: true, text: 'Élec (kWh)' }, grid: { drawOnChartArea: false } }
            }
        }
    });
});