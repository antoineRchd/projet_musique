# 🎧 Kafka Consumer - Spotify Analytics

Ce service consomme les données Spotify depuis Kafka et génère des analyses en temps réel.

## ✨ Fonctionnalités

### 📊 **Analytics en temps réel :**
- Traitement des tracks Spotify
- Statistiques par genre musical
- Statistiques par artiste
- Analyses des caractéristiques audio
- Dashboard temps réel

### 💾 **Sauvegarde automatique :**
- `spotify_analytics.json` - Analytics complètes
- `processed_tracks.csv` - Toutes les tracks traitées
- `top_genres.csv` - Top 20 genres
- `top_artists.csv` - Top 20 artistes

### 🎯 **Caractéristiques analysées :**
- **Danceability** : Aptitude à la danse
- **Energy** : Intensité énergétique
- **Valence** : Positivité musicale
- **Acousticness** : Caractère acoustique
- **Instrumentalness** : Niveau instrumental
- **Liveness** : Présence d'audience live
- **Speechiness** : Présence de parole
- **Loudness** : Volume sonore
- **Tempo** : Rythme (BPM)

## 🔧 Configuration

### Variables d'environnement :
```bash
KAFKA_BOOTSTRAP_SERVERS=kafka:9093
KAFKA_TOPIC=spotify-tracks
CONSUMER_GROUP=spotify-analytics-group
OUTPUT_DIR=/app/output
BATCH_SIZE=100
STATS_INTERVAL=30
```

## 🚀 Utilisation

### **Avec Docker Compose :**
```bash
# Le consumer démarre automatiquement
docker-compose up -d kafka-consumer

# Voir les logs du consumer
docker-compose logs -f kafka-consumer
```

### **En local :**
```bash
cd consumer
python consumer.py
```

## 📈 Dashboard temps réel

Le consumer affiche toutes les 30 secondes :

```
============================================================
🎵 SPOTIFY ANALYTICS DASHBOARD
============================================================
📊 Total Tracks Processed: 15420
⏱️  Processing Rate: 512.67 tracks/sec
🎭 Unique Genres: 89
👥 Unique Artists: 8934

🎶 Top 5 Genres:
  1. pop: 2156 tracks
  2. rock: 1843 tracks
  3. hip-hop: 1654 tracks
  4. electronic: 1432 tracks
  5. jazz: 1289 tracks

🎤 Top 5 Artists:
  1. The Beatles: 87 tracks
  2. Taylor Swift: 76 tracks
  3. Drake: 68 tracks
  4. Ed Sheeran: 62 tracks
  5. Ariana Grande: 59 tracks

🎵 Audio Features (Average):
  danceability: 0.567
  energy: 0.643
  valence: 0.512
  acousticness: 0.234
  instrumentalness: 0.089
============================================================
```

## 📂 Fichiers de sortie

### **spotify_analytics.json**
```json
{
  "summary": {
    "total_tracks_processed": 15420,
    "processing_duration_seconds": 30.15,
    "tracks_per_second": 512.67,
    "unique_genres": 89,
    "unique_artists": 8934
  },
  "top_genres": {
    "pop": 2156,
    "rock": 1843
  },
  "audio_features_avg": {
    "danceability": {
      "average": 0.567,
      "min": 0.0,
      "max": 0.983,
      "count": 15420
    }
  }
}
```

### **processed_tracks.csv**
```csv
track_name,artist,genre,popularity,processed_at,danceability,energy,valence
"Bohemian Rhapsody","Queen","rock",89,"2025-07-03T12:45:30",0.054,0.284,0.279
"Shape of You","Ed Sheeran","pop",93,"2025-07-03T12:45:31",0.825,0.652,0.931
```

## 🔄 Architecture

```
Kafka Topic          Consumer               Analytics
(spotify-tracks) --> [Processing] --> [Real-time Stats]
                         |                    |
                         v                    v
                   [Track Analysis]    [Periodic Save]
                         |                    |
                         v                    v
                   [Feature Extract]   [CSV/JSON Files]
```

## 🛠️ Développement

### **Ajouter de nouvelles analyses :**

1. Modifier `process_track()` pour extraire de nouvelles métriques
2. Mettre à jour `generate_analytics()` pour calculer les stats
3. Ajouter l'affichage dans `display_stats()`

### **Personnaliser la sauvegarde :**

Modifier `save_analytics()` pour ajouter de nouveaux formats de sortie.

## 🔍 Monitoring

- **Logs détaillés** : Progression, erreurs, connexions
- **Métriques temps réel** : Vitesse de traitement, volumes
- **Sauvegarde périodique** : Toutes les 100 tracks ou 30 secondes
- **Arrêt gracieux** : Ctrl+C pour arrêter proprement 