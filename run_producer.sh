#!/bin/bash
# Script pour exécuter le producteur Spotify Dataset

echo "🎵 Démarrage du producteur Spotify Dataset Kafka"
echo "=========================================="

# Vérifier si Docker Compose est lancé
if ! docker-compose ps | grep -q "kafka.*Up"; then
    echo "❌ Kafka n'est pas démarré. Démarrage de l'infrastructure..."
    docker-compose up -d
    echo "⏳ Attente du démarrage de Kafka..."
    sleep 30
else
    echo "✅ Kafka est déjà démarré"
fi

# Installer les dépendances si nécessaire
echo "📦 Vérification des dépendances..."
pip install -r requirements.txt

# Exécuter le producteur
echo "🚀 Exécution du producteur..."
cd producer
python test_local.py

echo "✅ Producteur terminé" 