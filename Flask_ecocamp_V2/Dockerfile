FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code
COPY . .

# Créer le dossier instance et copier config.cfg

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:8000", "wsgi:application"]
