/* Scroll hint */
const hint = document.getElementById('scrollHint');

window.addEventListener('scroll', () => {
    if (window.scrollY > 60) {
        hint.style.opacity = '0';
        hint.style.pointerEvents = 'none';
    }
});

hint.addEventListener('click', () => {
    window.scrollBy({ top: 400, behavior: 'smooth' });
});