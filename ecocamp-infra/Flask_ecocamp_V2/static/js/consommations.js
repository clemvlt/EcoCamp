document.addEventListener('DOMContentLoaded', function () {
    if (typeof rawData === 'undefined' || rawData.length === 0) return;

    // Les données arrivent du plus récent au plus ancien (ORDER BY DESC côté SQL)
    // On les inverse pour avoir l'ordre chronologique dans le graphique
    const datasetEau  = rawData.filter(d => d.id_type_flux === 4).reverse();
    const datasetElec = rawData.filter(d => d.id_type_flux === 3).reverse();

    // Mise à jour des cartes récapitulatives (dernier relevé = dernier élément après reverse)
    if (datasetEau.length > 0) {
        const dernierEau = datasetEau[datasetEau.length - 1].valeur;
        document.getElementById('valeurEau').textContent =
            (dernierEau !== null && dernierEau !== undefined ? dernierEau.toFixed(2) : '--') + " L";
    }
    if (datasetElec.length > 0) {
        const dernierElec = datasetElec[datasetElec.length - 1].valeur;
        document.getElementById('valeurElec').textContent =
            (dernierElec !== null && dernierElec !== undefined ? dernierElec.toFixed(2) : '--') + " kWh";
    }

    // Étiquettes de l'axe X — on prend le dataset le plus fourni comme référence
    const sourceLabels = datasetElec.length >= datasetEau.length ? datasetElec : datasetEau;
    const labels = sourceLabels.map(d => d.label.split(' (')[0]);

    const canvas = document.getElementById('consoChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Consommation Eau (L)',
                    data: datasetEau.map(d => d.valeur),
                    backgroundColor: 'rgba(0, 90, 150, 0.7)',
                    borderColor: 'rgba(0, 90, 150, 1)',
                    borderWidth: 1,
                    yAxisID: 'yEau'
                },
                {
                    label: 'Consommation Électricité (kWh)',
                    data: datasetElec.map(d => d.valeur),
                    backgroundColor: 'rgba(251, 192, 45, 0.7)',
                    borderColor: 'rgba(251, 192, 45, 1)',
                    borderWidth: 1,
                    yAxisID: 'yElec'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                title: {
                    display: true,
                    text: 'Consommations sur les 7 derniers jours'
                }
            },
            scales: {
                yEau: {
                    position: 'left',
                    title: { display: true, text: 'Eau (L)' },
                    beginAtZero: true
                },
                yElec: {
                    position: 'right',
                    title: { display: true, text: 'Élec (kWh)' },
                    beginAtZero: true,
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
});