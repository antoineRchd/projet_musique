FROM python:3.11-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code du producteur
COPY producer/ ./producer/

# Script d'initialisation : attente de Kafka puis publication
RUN echo '#!/bin/bash\n\
    echo "🎵 Attente de Kafka..."\n\
    while ! nc -z kafka 9093; do\n\
    echo "Kafka pas encore prêt, attente..."\n\
    sleep 5\n\
    done\n\
    echo "✅ Kafka est prêt !"\n\
    sleep 10\n\
    echo "🚀 Chargement des données Spotify..."\n\
    cd producer\n\
    python producer.py\n\
    echo "✅ Données chargées avec succès !"\n' > /app/load_spotify_data.sh

RUN chmod +x /app/load_spotify_data.sh

CMD ["/app/load_spotify_data.sh"] 