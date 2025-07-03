# Spotify Dataset Kafka Producer

Ce module télécharge le dataset Spotify depuis Kaggle et le publie dans Kafka.

## Configuration

Le producteur utilise les paramètres suivants par défaut :
- **Topic Kafka** : `spotify-tracks`
- **Serveurs Kafka** : `kafka:9092` (ou `localhost:9092` pour les tests locaux)
- **Taille des lots** : 1000 messages
- **Délai entre les lots** : 1 seconde

## Installation des dépendances

```bash
pip install -r ../requirements.txt
```

## Utilisation

### 1. Démarrer l'infrastructure avec Docker

```bash
# Depuis la racine du projet
docker-compose up -d
```

### 2. Exécuter le producteur

#### Option A : Exécution locale (recommandée pour les tests)

```bash
cd producer
python test_local.py
```

#### Option B : Exécution dans Docker

```bash
# Depuis la racine du projet
docker-compose exec spark python /app/producer/producer.py
```

### 3. Tester la consommation

Pour vérifier que les données sont bien publiées :

```bash
cd producer
python consumer_test.py --max-messages 5
```

## Fonctionnalités

### SpotifyDatasetProducer

- **Téléchargement automatique** : Télécharge le dataset depuis Kaggle
- **Connexion robuste** : Logique de retry pour la connexion Kafka
- **Publication par lots** : Traite les données par lots pour de meilleures performances
- **Logging complet** : Logs détaillés pour le debugging
- **Gestion d'erreurs** : Gestion des erreurs de publication individuelle

### Données publiées

Chaque message contient :
- **Données originales** : Toutes les colonnes du dataset Spotify
- **Métadonnées ajoutées** :
  - `timestamp` : Timestamp de publication
  - `record_id` : ID du record (index dans le dataset)
- **Clé** : `track_id` si disponible, sinon l'index

## Structure du dataset

Le dataset Spotify contient généralement :
- `track_id` : ID unique de la piste
- `track_name` : Nom de la piste
- `artists` : Artiste(s)
- `album_name` : Nom de l'album
- `popularity` : Score de popularité
- `danceability` : Mesure de dansabilité
- `energy` : Mesure d'énergie
- `valence` : Mesure de valence (positivité)
- Et d'autres caractéristiques audio...

## Monitoring

### Logs

Les logs incluent :
- Progression du téléchargement
- Statut de connexion Kafka
- Nombre de messages publiés/échoués
- Erreurs détaillées

### Métriques

- Nombre total de records traités
- Nombre de succès/échecs
- Temps de traitement

## Personnalisation

### Modifier le topic

```python
KAFKA_TOPIC = "mon-topic-spotify"
```

### Modifier la taille des lots

```python
BATCH_SIZE = 500  # Messages par lot
DELAY_BETWEEN_BATCHES = 2  # Secondes
```

### Modifier les serveurs Kafka

```python
KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092", "kafka2:9092"]
```

## Dépannage

### Erreur de connexion Kafka

1. Vérifier que Kafka est démarré :
   ```bash
   docker-compose ps
   ```

2. Vérifier les logs Kafka :
   ```bash
   docker-compose logs kafka
   ```

### Erreur de téléchargement Kaggle

1. Vérifier la configuration Kaggle API
2. S'assurer que le dataset existe et est accessible

### Erreur de mémoire

Pour de gros datasets, ajuster :
- `BATCH_SIZE` (réduire)
- `DELAY_BETWEEN_BATCHES` (augmenter)
- Configuration mémoire Docker

## Intégration avec Spark

Les données publiées peuvent être consommées par Spark Streaming :

```python
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "spotify-tracks") \
    .load()
``` 