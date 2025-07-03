# 🎵 Guide de démarrage rapide - Spotify Dataset Kafka

Ce guide vous permettra de rapidement intégrer le dataset Spotify dans Kafka.

## 🚀 Démarrage rapide

### 1. Démarrer l'infrastructure

```bash
docker-compose up -d
```

### 2. Publier le dataset Spotify dans Kafka

```bash
./run_producer.sh
```

### 3. Tester la consommation

```bash
./test_consumer.sh
```

## 📝 Étapes détaillées

### Étape 1 : Préparation

1. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

2. **Démarrer les services Docker**
   ```bash
   docker-compose up -d
   ```

   Services démarrés :
   - ✅ Zookeeper (port 2181)
   - ✅ Kafka (port 9092)
   - ✅ Hadoop NameNode (port 9870)
   - ✅ Hadoop DataNode
   - ✅ Spark Master (port 8080)

### Étape 2 : Publication des données

Le producteur va automatiquement :
1. 📥 Télécharger le dataset Spotify depuis Kaggle
2. 📊 Charger les données CSV
3. 🚀 Publier chaque piste dans Kafka (topic: `spotify-tracks`)

```bash
cd producer
python test_local.py
```

### Étape 3 : Vérification

Tester que les données sont bien publiées :

```bash
cd producer
python consumer_test.py --max-messages 5
```

## 🎯 Utilisation avancée

### Configuration personnalisée

Modifier les paramètres dans `producer/producer.py` :

```python
# Topic Kafka
KAFKA_TOPIC = "spotify-tracks"

# Taille des lots
BATCH_SIZE = 1000

# Délai entre les lots
DELAY_BETWEEN_BATCHES = 1
```

### Consommation avec Spark

Les données peuvent être consommées par Spark Streaming :

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("SpotifyStreaming") \
    .getOrCreate()

# Lire depuis Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "spotify-tracks") \
    .load()

# Décoder les données JSON
spotify_df = df.select(
    col("key").cast("string"),
    from_json(col("value").cast("string"), spotify_schema).alias("data")
).select("key", "data.*")
```

## 🎮 Interfaces web

Une fois démarré, vous pouvez accéder à :

- **Spark UI** : http://localhost:8080
- **Hadoop NameNode** : http://localhost:9870

## 🔧 Dépannage

### Kafka ne démarre pas

```bash
# Vérifier les logs
docker-compose logs kafka

# Redémarrer les services
docker-compose restart
```

### Erreur de téléchargement Kaggle

1. Vérifier la configuration de l'API Kaggle
2. S'assurer d'avoir accepté les conditions du dataset

### Erreur de mémoire

Pour de gros datasets :
- Réduire `BATCH_SIZE`
- Augmenter `DELAY_BETWEEN_BATCHES`
- Augmenter la mémoire Docker

## 📊 Données du dataset

Le dataset Spotify contient :
- **Métadonnées** : nom, artiste, album, popularité
- **Caractéristiques audio** : danceability, energy, valence, tempo
- **Informations techniques** : durée, clé, mode, etc.

## 🔄 Prochaines étapes

1. **Traitement en temps réel** avec Spark Streaming
2. **Stockage** dans HDFS
3. **Analyse** avec des jobs Spark
4. **Visualisation** des données

## 🆘 Support

En cas de problème :
1. Vérifier les logs : `docker-compose logs [service]`
2. Consulter la documentation dans `producer/README.md`
3. Tester individuellement chaque composant 