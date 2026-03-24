// Simulation de mise à jour des données en temps réel
function updateData() {
    const water = (Math.random() * 100).toFixed(1);
    const elec = (Math.random() * 50).toFixed(1);

    document.getElementById('water-val').innerText = water + " L";
    document.getElementById('elec-val').innerText = elec + " kWh";
}

// Mise à jour toutes les 3 secondes
setInterval(updateData, 3000);
updateData();

// Configuration d'un petit graphique de test avec Chart.js
const ctx = document.getElementById('myChart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['08:00', '10:00', '12:00', '14:00', '16:00'],
        datasets: [{
            label: 'Consommation Énergie',
            data: [12, 19, 3, 5, 2],
            borderColor: '#2e7d32',
            tension: 0.3
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});