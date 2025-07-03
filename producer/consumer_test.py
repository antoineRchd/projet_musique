#!/usr/bin/env python3
"""
Simple Kafka Consumer for testing Spotify dataset
Consumes messages from the spotify-tracks topic
"""

import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Configuration
KAFKA_TOPIC = "spotify-tracks"
KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092"]

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SpotifyDatasetConsumer:
    def __init__(self, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, topic=KAFKA_TOPIC):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None

    def connect_kafka(self):
        """Initialize Kafka consumer"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                key_deserializer=lambda m: m.decode("utf-8") if m else None,
                auto_offset_reset="earliest",  # Start from beginning
                enable_auto_commit=True,
                group_id="spotify-test-group",
            )
            logger.info(f"Successfully connected to Kafka topic: {self.topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            return False

    def consume_messages(self, max_messages=10):
        """Consume and display messages"""
        if not self.consumer:
            logger.error("Kafka consumer not initialized")
            return

        try:
            logger.info(f"Starting to consume messages from topic '{self.topic}'")
            logger.info(f"Will display up to {max_messages} messages")

            message_count = 0

            for message in self.consumer:
                try:
                    key = message.key
                    value = message.value

                    logger.info(f"Message {message_count + 1}:")
                    logger.info(f"  Key: {key}")
                    logger.info(f"  Partition: {message.partition}")
                    logger.info(f"  Offset: {message.offset}")

                    # Display track info if available
                    if isinstance(value, dict):
                        track_name = value.get("track_name", "Unknown")
                        artist_name = value.get("artists", "Unknown")
                        album_name = value.get("album_name", "Unknown")

                        logger.info(f"  Track: {track_name}")
                        logger.info(f"  Artist: {artist_name}")
                        logger.info(f"  Album: {album_name}")

                        # Show some audio features if available
                        if "danceability" in value:
                            logger.info(
                                f"  Danceability: {value.get('danceability', 'N/A')}"
                            )
                        if "energy" in value:
                            logger.info(f"  Energy: {value.get('energy', 'N/A')}")
                        if "valence" in value:
                            logger.info(f"  Valence: {value.get('valence', 'N/A')}")

                    logger.info("-" * 50)

                    message_count += 1

                    if message_count >= max_messages:
                        logger.info(
                            f"Reached maximum messages ({max_messages}). Stopping."
                        )
                        break

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
        finally:
            if self.consumer:
                self.consumer.close()
                logger.info("Consumer closed")

    def run(self, max_messages=10):
        """Main execution method"""
        logger.info("Starting Spotify Dataset Kafka Consumer")

        if not self.connect_kafka():
            logger.error("Failed to connect to Kafka. Exiting.")
            return

        self.consume_messages(max_messages)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Consume Spotify dataset from Kafka")
    parser.add_argument(
        "--max-messages",
        type=int,
        default=10,
        help="Maximum number of messages to display (default: 10)",
    )
    parser.add_argument(
        "--servers",
        type=str,
        default="localhost:9092",
        help="Kafka bootstrap servers (default: localhost:9092)",
    )

    args = parser.parse_args()

    bootstrap_servers = args.servers.split(",")

    consumer = SpotifyDatasetConsumer(
        bootstrap_servers=bootstrap_servers, topic=KAFKA_TOPIC
    )

    consumer.run(max_messages=args.max_messages)


if __name__ == "__main__":
    main()
