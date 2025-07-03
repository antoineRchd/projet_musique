# 🏗️ Architecture Kafka Producer-Consumer - Projet Spotify

Architecture complète pour le traitement des données Spotify avec Kafka.

## 🎯 Vue d'ensemble

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  KAFKA PRODUCER │───▶│      KAFKA      │───▶│  KAFKA CONSUMER │
│                 │    │                 │    │                 │
│  • Download     │    │  Topic:         │    │  • Analytics    │
│  • Transform    │    │  spotify-tracks │    │  • Dashboard    │
│  • Publish      │    │                 │    │  • Export       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
       │                         │                         │
       ▼                         ▼                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kaggle API    │    │  Zookeeper      │    │  Output Files   │
│   (Dataset)     │    │  (Coordination) │    │  (CSV/JSON)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Composants

### 📤 **Kafka Producer** (`kafka-producer`)

**Rôle :** Acquisition et publication des données

**Fonctionnalités :**
- ✅ Téléchargement automatique du dataset Spotify (114k tracks)
- ✅ Chargement et validation des données CSV
- ✅ Publication par lots (1000 messages/lot)
- ✅ Vérification des données existantes (évite les doublons)
- ✅ Gestion d'erreurs robuste avec retry
- ✅ Logs détaillés de progression

**Configuration :**
```yaml
environment:
  - KAFKA_BOOTSTRAP_SERVERS=kafka:9093
  - KAFKA_TOPIC=spotify-tracks
  - PRODUCER_MODE=true
  - BATCH_SIZE=1000
  - DELAY_BETWEEN_BATCHES=1
```

**Démarrage :** Une seule fois au démarrage du système

### 📥 **Kafka Consumer** (`kafka-consumer`)

**Rôle :** Consommation et analyse des données

**Fonctionnalités :**
- ✅ Consommation en temps réel des messages Kafka
- ✅ Analytics avancées (genres, artistes, audio features)
- ✅ Dashboard temps réel (mise à jour toutes les 30s)
- ✅ Sauvegarde automatique (CSV, JSON)
- ✅ Arrêt gracieux (Ctrl+C)
- ✅ Monitoring des performances

**Configuration :**
```yaml
environment:
  - KAFKA_BOOTSTRAP_SERVERS=kafka:9093
  - KAFKA_TOPIC=spotify-tracks
  - CONSUMER_GROUP=spotify-analytics-group
  - OUTPUT_DIR=/app/output
  - BATCH_SIZE=100
  - STATS_INTERVAL=30
```

**Démarrage :** Continue en arrière-plan (restart: unless-stopped)

## 🚀 Démarrage complet

```bash
# 1. Démarrer toute l'infrastructure
docker-compose up -d

# 2. Vérifier les logs du producer (charge les données)
docker-compose logs -f kafka-producer

# 3. Vérifier les logs du consumer (traite les données)
docker-compose logs -f kafka-consumer

# 4. Accéder à l'interface Kafka UI
# http://localhost:8090
```

## 📊 Flux de données

### **1. Phase d'acquisition (Producer)**
```
Kaggle API ──▶ Download ──▶ CSV Load ──▶ JSON Transform ──▶ Kafka Publish
    │              │           │              │               │
    8.17MB     114k tracks  21 columns    JSON format    1000/batch
```

### **2. Phase de traitement (Consumer)**
```
Kafka Poll ──▶ Track Process ──▶ Analytics ──▶ Dashboard ──▶ File Save
    │              │               │           │            │
Real-time     Feature Extract  Stats Calc   Display    CSV/JSON
```

## 🎵 Structure des données

### **Message Kafka :**
```json
{
  "track_id": "5SuOikwiRyPMVoIQDJUgSV",
  "track_name": "Comedy",
  "artists": "Gen Hoshino",
  "album_name": "Comedy",
  "popularity": 73,
  "duration_ms": 230666,
  "explicit": false,
  "danceability": 0.676,
  "energy": 0.461,
  "valence": 0.715,
  "tempo": 87.917,
  "track_genre": "acoustic",
  "timestamp": 1751539166,
  "record_id": 0
}
```

### **Analytics générées :**
- **Summary** : Métriques globales
- **Top Genres** : Classification musicale
- **Top Artists** : Popularité des artistes
- **Audio Features** : Caractéristiques moyennes

## 🔄 Gestion des erreurs

### **Producer :**
- Retry automatique (5 tentatives)
- Skip des messages défaillants
- Logs détaillés des erreurs
- Graceful shutdown

### **Consumer :**
- Timeout non-bloquant (1 seconde)
- Continue processing en cas d'erreur
- Sauvegarde périodique des données
- Signal handling (SIGINT, SIGTERM)

## 📈 Monitoring

### **Métriques Producer :**
- Messages publiés/échecs
- Vitesse de publication
- Progression du dataset
- Statut connexion Kafka

### **Métriques Consumer :**
- Tracks traitées
- Vitesse de traitement
- Genres/Artistes uniques
- Features audio moyennes

## 🌐 Interfaces

### **Kafka UI :** http://localhost:8090
- Topics et partitions
- Messages en temps réel
- Consumer groups
- Métriques Kafka

### **Hadoop NameNode :** http://localhost:9870
- HDFS status
- Cluster information

### **Spark UI :** http://localhost:8080
- Applications Spark
- Jobs et stages

## 🎛️ Configuration avancée

### **Kafka Topics :**
```bash
# Créer topic avec plus de partitions
KAFKA_CREATE_TOPICS: "spotify-tracks:3:1"

# Modifier retention
KAFKA_LOG_RETENTION_HOURS=72
```

### **Performance :**
```yaml
# Producer
BATCH_SIZE=2000
DELAY_BETWEEN_BATCHES=0.5

# Consumer  
BATCH_SIZE=500
STATS_INTERVAL=10
```

## 🔧 Maintenance

### **Redémarrer services :**
```bash
# Producer seulement
docker-compose restart kafka-producer

# Consumer seulement  
docker-compose restart kafka-consumer

# Tout redémarrer
docker-compose restart
```

### **Nettoyer les données :**
```bash
# Supprimer volumes (données perdues)
docker-compose down -v

# Nettoyer les fichiers de sortie
rm -rf output/*
```

## 🎯 Cas d'usage

### **Analytics temps réel :**
- Dashboard live des données musicales
- Monitoring de tendances
- Détection d'anomalies

### **Data Science :**
- Analyse des préférences musicales  
- Machine Learning sur audio features
- Recommandations personnalisées

### **Big Data Pipeline :**
- Ingestion de données massives
- Traitement distribué avec Spark
- Stockage HDFS pour analytics batch

## 🚧 Extensions possibles

1. **Multiple Consumers** : Différents types d'analyses
2. **Stream Processing** : Spark Streaming integration  
3. **Machine Learning** : Modèles prédictifs en temps réel
4. **APIs REST** : Exposition des analytics
5. **Visualizations** : Dashboards interactifs
6. **Alerting** : Notifications sur événements 