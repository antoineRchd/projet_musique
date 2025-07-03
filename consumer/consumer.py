#!/usr/bin/env python3
"""
Spotify Dataset Kafka Consumer
Consumes Spotify tracks from Kafka and performs real-time analytics
"""

import json
import time
import logging
import os
import pandas as pd
from collections import defaultdict, Counter
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from datetime import datetime
import threading
import signal
import sys

# Configuration with environment variable support
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "spotify-tracks")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(
    ","
)
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "spotify-analytics-group")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/output")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
STATS_INTERVAL = int(os.getenv("STATS_INTERVAL", "30"))  # seconds

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SpotifyDataAnalyzer:
    def __init__(self):
        self.bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS
        self.topic = KAFKA_TOPIC
        self.consumer_group = CONSUMER_GROUP
        self.output_dir = OUTPUT_DIR
        self.consumer = None
        self.running = True

        # Analytics data
        self.tracks_processed = 0
        self.start_time = time.time()
        self.genre_stats = Counter()
        self.artist_stats = Counter()
        self.audio_features = defaultdict(list)
        self.processed_tracks = []

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

    def connect_kafka(self):
        """Initialize Kafka consumer with retry logic"""
        max_retries = 5
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.bootstrap_servers,
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                    key_deserializer=lambda m: m.decode("utf-8") if m else None,
                    auto_offset_reset="earliest",
                    enable_auto_commit=True,
                    group_id=self.consumer_group,
                    consumer_timeout_ms=1000,  # 1 second timeout for non-blocking
                )
                logger.info(
                    f"Successfully connected to Kafka at {self.bootstrap_servers}"
                )
                logger.info(f"Consuming from topic: {self.topic}")
                logger.info(f"Consumer group: {self.consumer_group}")
                return True
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed to connect to Kafka: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Could not connect to Kafka.")
                    return False

        return False

    def process_track(self, track_data):
        """Process a single track and extract analytics"""
        try:
            # Extract basic info
            track_name = track_data.get("track_name", "Unknown")
            artist = track_data.get("artists", "Unknown")
            genre = track_data.get("track_genre", "Unknown")
            popularity = track_data.get("popularity", 0)

            # Update counters
            self.genre_stats[genre] += 1
            self.artist_stats[artist] += 1

            # Collect audio features
            audio_features = [
                "danceability",
                "energy",
                "valence",
                "acousticness",
                "instrumentalness",
                "liveness",
                "speechiness",
                "loudness",
                "tempo",
            ]

            track_features = {}
            for feature in audio_features:
                if feature in track_data:
                    value = track_data[feature]
                    self.audio_features[feature].append(value)
                    track_features[feature] = value

            # Store processed track
            processed_track = {
                "track_name": track_name,
                "artist": artist,
                "genre": genre,
                "popularity": popularity,
                "processed_at": datetime.now().isoformat(),
                **track_features,
            }

            self.processed_tracks.append(processed_track)
            self.tracks_processed += 1

            # Log progress every 100 tracks
            if self.tracks_processed % 100 == 0:
                logger.info(f"Processed {self.tracks_processed} tracks")

            return True

        except Exception as e:
            logger.error(f"Error processing track: {e}")
            return False

    def generate_analytics(self):
        """Generate comprehensive analytics"""
        if self.tracks_processed == 0:
            return {}

        analytics = {
            "summary": {
                "total_tracks_processed": self.tracks_processed,
                "processing_duration_seconds": time.time() - self.start_time,
                "tracks_per_second": self.tracks_processed
                / (time.time() - self.start_time),
                "unique_genres": len(self.genre_stats),
                "unique_artists": len(self.artist_stats),
                "generated_at": datetime.now().isoformat(),
            },
            "top_genres": dict(self.genre_stats.most_common(10)),
            "top_artists": dict(self.artist_stats.most_common(10)),
            "audio_features_avg": {},
        }

        # Calculate average audio features
        for feature, values in self.audio_features.items():
            if values:
                analytics["audio_features_avg"][feature] = {
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }

        return analytics

    def save_analytics(self):
        """Save analytics to files"""
        try:
            analytics = self.generate_analytics()

            # Save analytics JSON
            analytics_file = os.path.join(self.output_dir, "spotify_analytics.json")
            with open(analytics_file, "w") as f:
                json.dump(analytics, f, indent=2)

            # Save processed tracks CSV
            if self.processed_tracks:
                tracks_file = os.path.join(self.output_dir, "processed_tracks.csv")
                df = pd.DataFrame(self.processed_tracks)
                df.to_csv(tracks_file, index=False)

            # Save top genres CSV
            genres_file = os.path.join(self.output_dir, "top_genres.csv")
            genres_df = pd.DataFrame(
                [
                    {"genre": genre, "count": count}
                    for genre, count in self.genre_stats.most_common(20)
                ]
            )
            genres_df.to_csv(genres_file, index=False)

            # Save top artists CSV
            artists_file = os.path.join(self.output_dir, "top_artists.csv")
            artists_df = pd.DataFrame(
                [
                    {"artist": artist, "count": count}
                    for artist, count in self.artist_stats.most_common(20)
                ]
            )
            artists_df.to_csv(artists_file, index=False)

            logger.info(f"Analytics saved to {self.output_dir}")

        except Exception as e:
            logger.error(f"Error saving analytics: {e}")

    def display_stats(self):
        """Display real-time statistics"""
        analytics = self.generate_analytics()

        print("\n" + "=" * 60)
        print("🎵 SPOTIFY ANALYTICS DASHBOARD")
        print("=" * 60)

        # Summary
        summary = analytics.get("summary", {})
        print(f"📊 Total Tracks Processed: {summary.get('total_tracks_processed', 0)}")
        print(
            f"⏱️  Processing Rate: {summary.get('tracks_per_second', 0):.2f} tracks/sec"
        )
        print(f"🎭 Unique Genres: {summary.get('unique_genres', 0)}")
        print(f"👥 Unique Artists: {summary.get('unique_artists', 0)}")

        # Top genres
        top_genres = analytics.get("top_genres", {})
        if top_genres:
            print("\n🎶 Top 5 Genres:")
            for i, (genre, count) in enumerate(list(top_genres.items())[:5], 1):
                print(f"  {i}. {genre}: {count} tracks")

        # Top artists
        top_artists = analytics.get("top_artists", {})
        if top_artists:
            print("\n🎤 Top 5 Artists:")
            for i, (artist, count) in enumerate(list(top_artists.items())[:5], 1):
                print(f"  {i}. {artist}: {count} tracks")

        # Audio features
        audio_avg = analytics.get("audio_features_avg", {})
        if audio_avg:
            print("\n🎵 Audio Features (Average):")
            for feature, stats in audio_avg.items():
                print(f"  {feature}: {stats['average']:.3f}")

        print("=" * 60)

    def stats_worker(self):
        """Background worker to display stats periodically"""
        while self.running:
            time.sleep(STATS_INTERVAL)
            if self.running and self.tracks_processed > 0:
                self.display_stats()
                self.save_analytics()

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal. Gracefully shutting down...")
        self.running = False
        if self.consumer:
            self.consumer.close()
        self.save_analytics()
        sys.exit(0)

    def run(self):
        """Main execution method"""
        logger.info("Starting Spotify Dataset Kafka Consumer")

        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Connect to Kafka
        if not self.connect_kafka():
            logger.error("Failed to connect to Kafka. Exiting.")
            return

        # Start stats worker thread
        stats_thread = threading.Thread(target=self.stats_worker, daemon=True)
        stats_thread.start()

        logger.info("Consumer started. Processing messages...")
        logger.info("Press Ctrl+C to stop gracefully")

        try:
            batch_count = 0
            for message in self.consumer:
                if not self.running:
                    break

                try:
                    track_data = message.value
                    if self.process_track(track_data):
                        batch_count += 1

                        # Save periodically
                        if batch_count >= BATCH_SIZE:
                            self.save_analytics()
                            batch_count = 0

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
        finally:
            logger.info("Shutting down consumer...")
            if self.consumer:
                self.consumer.close()
            self.save_analytics()
            logger.info("Consumer shutdown complete")


def main():
    """Main function"""
    analyzer = SpotifyDataAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()
