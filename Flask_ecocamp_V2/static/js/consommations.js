document.addEventListener('DOMContentLoaded', function () {
    if (typeof rawData === 'undefined' || rawData.length === 0) return;

    const joursSemaine = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"];

    // Helper : transforme "DD/MM HH:mm" en label lisible avec le jour
    function buildLabel(labelStr) {
        const parties = labelStr.split(' ');
        const dateParts = parties[0].split('/');
        const dateObj = new Date(2026, parseInt(dateParts[1]) - 1, parseInt(dateParts[0]));
        return joursSemaine[dateObj.getDay()] + ' ' + parties[0];
    }

    // ── Filtrage par type, ordre chronologique (les données arrivent DESC) ──
    const dataEau  = rawData.filter(d => d.id_type_flux === 4).reverse();
    const dataElec = rawData.filter(d => d.id_type_flux === 3).reverse();

    // ── Mise à jour des KPI cards ──
    if (dataEau.length > 0) {
        const v = dataEau[dataEau.length - 1].valeur;
        document.getElementById('valeurEau').textContent = (v || 0).toFixed(2) + ' L';
    }
    if (dataElec.length > 0) {
        const v = dataElec[dataElec.length - 1].valeur;
        document.getElementById('valeurElec').textContent = (v || 0).toFixed(2) + ' kWh';
    }

    // ── Thème commun sombre ──
    const darkGrid  = 'rgba(255,255,255,.06)';
    const tickColor = '#64748b';
    const legendColor = '#94a3b8';

    // ══════════════════════════════════════════
    // GRAPHIQUE EAU
    // ══════════════════════════════════════════
    const canvasEau = document.getElementById('chartEau');
    if (canvasEau && dataEau.length > 0) {
        new Chart(canvasEau.getContext('2d'), {
            type: 'bar',
            data: {
                labels: dataEau.map(d => buildLabel(d.label)),
                datasets: [{
                    label: 'Eau (L)',
                    data: dataEau.map(d => d.valeur),
                    backgroundColor: '#0b59a2',
                    borderColor:     '#0b59a2',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: legendColor } },
                    title:  { display: false }
                },
                scales: {
                    x: {
                        ticks: { color: tickColor },
                        grid:  { color: darkGrid }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { color: tickColor },
                        grid:  { color: darkGrid },
                        title: { display: true, text: 'Litres (L)', color: tickColor }
                    }
                }
            }
        });
    } else if (canvasEau && dataEau.length === 0) {
        // Affiche un message vide dans le canvas
        const ctx = canvasEau.getContext('2d');
        ctx.fillStyle = '#4b5563';
        ctx.font = '14px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Aucune donnée eau sur 7 jours', canvasEau.width / 2, canvasEau.height / 2);
    }

    // ══════════════════════════════════════════
    // GRAPHIQUE ÉLECTRICITÉ
    // ══════════════════════════════════════════
    const canvasElec = document.getElementById('chartElec');
    if (canvasElec && dataElec.length > 0) {
        new Chart(canvasElec.getContext('2d'), {
            type: 'bar',
            data: {
                labels: dataElec.map(d => buildLabel(d.label)),
                datasets: [{
                    label: 'Électricité (kWh)',
                    data: dataElec.map(d => d.valeur),
                    backgroundColor: 'rgba(251,191,36,0.75)',
                    borderColor:     'rgba(251,191,36,1)',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: legendColor } },
                    title:  { display: false }
                },
                scales: {
                    x: {
                        ticks: { color: tickColor },
                        grid:  { color: darkGrid }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { color: tickColor },
                        grid:  { color: darkGrid },
                        title: { display: true, text: 'kWh', color: tickColor }
                    }
                }
            }
        });
    } else if (canvasElec && dataElec.length === 0) {
        const ctx = canvasElec.getContext('2d');
        ctx.fillStyle = '#4b5563';
        ctx.font = '14px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Aucune donnée électricité sur 7 jours', canvasElec.width / 2, canvasElec.height / 2);
    }
});