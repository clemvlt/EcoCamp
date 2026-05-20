// Système de notifications toast (bas à droite avec barre de progression)

class Toast {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Créer le conteneur s'il n'existe pas
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }

    show(message, type = 'success', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // Icône selon le type
        let icon = '';
        switch(type) {
            case 'success':
                icon = '✅';
                break;
            case 'error':
                icon = '❌';
                break;
            case 'info':
                icon = 'ℹ️';
                break;
            default:
                icon = '✅';
        }
        
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon">${icon}</div>
                <div class="toast-message">${message}</div>
            </div>
            <div class="toast-progress">
                <div class="toast-progress-bar" style="animation-duration: ${duration}ms"></div>
            </div>
        `;
        
        this.container.appendChild(toast);
        
        // Fermer au clic
        toast.addEventListener('click', () => {
            this.close(toast);
        });
        
        // Fermeture automatique
        setTimeout(() => {
            this.close(toast);
        }, duration);
    }

    close(toast) {
        toast.classList.add('hide');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 300);
    }

    success(message, duration = 3000) {
        this.show(message, 'success', duration);
    }

    error(message, duration = 3000) {
        this.show(message, 'error', duration);
    }

    info(message, duration = 3000) {
        this.show(message, 'info', duration);
    }
}

// Instance globale
const toast = new Toast();