document.addEventListener('DOMContentLoaded', function () {
    if (typeof rawData === 'undefined' || rawData.length === 0) return;

    const joursSemaine = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"];

    function buildLabel(labelStr) {
        const parties = labelStr.split(' ');
        const dateParts = parties[0].split('/');
        const dateObj = new Date(2026, parseInt(dateParts[1]) - 1, parseInt(dateParts[0]));
        return joursSemaine[dateObj.getDay()] + ' ' + parties[0];
    }

    // Données triées chronologiquement par type
    const dataEau  = rawData.filter(d => d.id_type_flux === 4).reverse();
    const dataElec = rawData.filter(d => d.id_type_flux === 3).reverse();

    // ── KPI : dernier index brut ──
    if (dataEau.length > 0) {
        const v = dataEau[dataEau.length - 1].index;
        document.getElementById('valeurEau').textContent = (v || 0).toFixed(2) + ' L';
    }
    if (dataElec.length > 0) {
        const v = dataElec[dataElec.length - 1].index;
        document.getElementById('valeurElec').textContent = (v || 0).toFixed(2) + ' kWh';
    }

    // ── Calcul conso journalière = index[j] - index[j-1] ──
    function calcDelta(data) {
        return data.map((d, i) => {
            if (i === 0) return { label: d.label, valeur: 0 };
            const delta = d.index - data[i - 1].index;
            return { label: d.label, valeur: delta >= 0 ? parseFloat(delta.toFixed(2)) : 0 };
        }).slice(1); // on retire le premier point (pas de J-1)
    }

    const deltaEau  = calcDelta(dataEau);
    const deltaElec = calcDelta(dataElec);

    const darkGrid    = 'rgba(255,255,255,.06)';
    const tickColor   = '#64748b';
    const legendColor = '#94a3b8';

    // ══ GRAPHIQUE EAU ══
    const canvasEau = document.getElementById('chartEau');
    if (canvasEau && deltaEau.length > 0) {
        new Chart(canvasEau.getContext('2d'), {
            type: 'bar',
            data: {
                labels: deltaEau.map(d => buildLabel(d.label)),
                datasets: [{
                    label: 'Eau (L)',
                    data: deltaEau.map(d => d.valeur),
                    backgroundColor: '#0b59a2',
                    borderColor:     '#0b59a2',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: legendColor } } },
                scales: {
                    x: { ticks: { color: tickColor }, grid: { color: darkGrid } },
                    y: {
                        beginAtZero: true,
                        ticks: { color: tickColor },
                        grid:  { color: darkGrid },
                        title: { display: true, text: 'Litres (L)', color: tickColor }
                    }
                }
            }
        });
    } else if (canvasEau) {
        const ctx = canvasEau.getContext('2d');
        ctx.fillStyle = '#4b5563';
        ctx.font = '14px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Aucune donnée eau sur 7 jours', canvasEau.width / 2, canvasEau.height / 2);
    }

    // ══ GRAPHIQUE ÉLECTRICITÉ ══
    const canvasElec = document.getElementById('chartElec');
    if (canvasElec && deltaElec.length > 0) {
        new Chart(canvasElec.getContext('2d'), {
            type: 'bar',
            data: {
                labels: deltaElec.map(d => buildLabel(d.label)),
                datasets: [{
                    label: 'Électricité (kWh)',
                    data: deltaElec.map(d => d.valeur),
                    backgroundColor: 'rgba(251,191,36,0.75)',
                    borderColor:     'rgba(251,191,36,1)',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: legendColor } } },
                scales: {
                    x: { ticks: { color: tickColor }, grid: { color: darkGrid } },
                    y: {
                        beginAtZero: true,
                        ticks: { color: tickColor },
                        grid:  { color: darkGrid },
                        title: { display: true, text: 'kWh', color: tickColor }
                    }
                }
            }
        });
    } else if (canvasElec) {
        const ctx = canvasElec.getContext('2d');
        ctx.fillStyle = '#4b5563';
        ctx.font = '14px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Aucune donnée électricité sur 7 jours', canvasElec.width / 2, canvasElec.height / 2);
    }
});