#!/bin/bash
# Script pour tester le consommateur Spotify Dataset

echo "🎧 Test du consommateur Spotify Dataset Kafka"
echo "=============================================="

# Vérifier si Docker Compose est lancé
if ! docker-compose ps | grep -q "kafka.*Up"; then
    echo "❌ Kafka n'est pas démarré. Veuillez démarrer l'infrastructure d'abord:"
    echo "   docker-compose up -d"
    exit 1
else
    echo "✅ Kafka est démarré"
fi

# Installer les dépendances si nécessaire
echo "📦 Vérification des dépendances..."
pip install -r requirements.txt

# Exécuter le consommateur
echo "🎵 Consommation des messages (Ctrl+C pour arrêter)..."
cd producer
python consumer_test.py --max-messages 10

echo "✅ Test du consommateur terminé" 