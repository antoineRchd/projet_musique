#!/usr/bin/env python3
"""
Spotify Dataset Kafka Producer
Downloads Spotify tracks dataset from Kaggle and publishes to Kafka
"""

import json
import time
import logging
import os
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaError
import kagglehub

# Configuration with environment variable support
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "spotify-tracks")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(
    ","
)
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
DELAY_BETWEEN_BATCHES = int(os.getenv("DELAY_BETWEEN_BATCHES", "1"))  # seconds

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SpotifyDatasetProducer:
    def __init__(self, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, topic=KAFKA_TOPIC):
        self.topic = topic
        self.producer = None
        self.bootstrap_servers = bootstrap_servers

    def connect_kafka(self):
        """Initialize Kafka producer with retry logic"""
        max_retries = 5
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    key_serializer=lambda k: k.encode("utf-8") if k else None,
                    acks="all",
                    retries=3,
                    batch_size=16384,
                    linger_ms=10,
                    buffer_memory=33554432,
                )
                logger.info(
                    f"Successfully connected to Kafka at {self.bootstrap_servers}"
                )
                return True
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed to connect to Kafka: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Could not connect to Kafka.")
                    return False

        return False

    def download_dataset(self):
        """Download Spotify dataset from Kaggle"""
        try:
            logger.info("Starting dataset download from Kaggle...")
            path = kagglehub.dataset_download("maharshipandya/-spotify-tracks-dataset")
            logger.info(f"Dataset downloaded to: {path}")
            return path
        except Exception as e:
            logger.error(f"Error downloading dataset: {e}")
            return None

    def load_dataset(self, dataset_path):
        """Load and prepare dataset for streaming"""
        try:
            # Find CSV files in the dataset directory
            csv_files = []
            for root, dirs, files in os.walk(dataset_path):
                for file in files:
                    if file.endswith(".csv"):
                        csv_files.append(os.path.join(root, file))

            if not csv_files:
                logger.error("No CSV files found in the dataset")
                return None

            # Load the first CSV file (assuming main dataset)
            main_csv = csv_files[0]
            logger.info(f"Loading dataset from: {main_csv}")

            df = pd.read_csv(main_csv)
            logger.info(f"Dataset loaded successfully. Shape: {df.shape}")
            logger.info(f"Columns: {list(df.columns)}")

            return df

        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            return None

    def check_if_data_exists(self):
        """Check if data already exists in Kafka topic"""
        try:
            from kafka import KafkaConsumer

            consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                consumer_timeout_ms=5000,
                auto_offset_reset="earliest",
                group_id="check-data-group",
            )

            message_count = 0
            for message in consumer:
                message_count += 1
                if message_count >= 10:  # Just check if we have some data
                    break

            consumer.close()
            logger.info(f"Found {message_count} existing messages in topic")
            return message_count > 0

        except Exception as e:
            logger.warning(f"Could not check existing data: {e}")
            return False

    def publish_to_kafka(self, df):
        """Publish dataset to Kafka topic"""
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False

        try:
            total_records = len(df)
            logger.info(
                f"Starting to publish {total_records} records to Kafka topic '{self.topic}'"
            )

            published_count = 0
            failed_count = 0

            for index, row in df.iterrows():
                try:
                    # Convert row to dictionary
                    record = row.to_dict()

                    # Add metadata
                    record["timestamp"] = int(time.time())
                    record["record_id"] = index

                    # Use track_id as key if available, otherwise use index
                    key = str(record.get("track_id", index))

                    # Send to Kafka
                    future = self.producer.send(self.topic, key=key, value=record)

                    # Optional: wait for confirmation (slower but more reliable)
                    # future.get(timeout=10)

                    published_count += 1

                    # Log progress
                    if published_count % BATCH_SIZE == 0:
                        logger.info(
                            f"Published {published_count}/{total_records} records"
                        )
                        self.producer.flush()
                        time.sleep(DELAY_BETWEEN_BATCHES)

                except Exception as e:
                    logger.error(f"Error publishing record {index}: {e}")
                    failed_count += 1
                    continue

            # Flush remaining messages
            self.producer.flush()

            logger.info(
                f"Publishing completed. Success: {published_count}, Failed: {failed_count}"
            )
            return True

        except Exception as e:
            logger.error(f"Error during publishing: {e}")
            return False

    def run(self):
        """Main execution method"""
        logger.info("Starting Spotify Dataset Kafka Producer")
        logger.info(f"Using Kafka servers: {self.bootstrap_servers}")
        logger.info(f"Using topic: {self.topic}")

        # Connect to Kafka
        if not self.connect_kafka():
            logger.error("Failed to connect to Kafka. Exiting.")
            return

        # Check if data already exists
        if self.check_if_data_exists():
            logger.info(
                "Data already exists in Kafka topic. Skipping download and upload."
            )
            return

        # Download dataset
        dataset_path = self.download_dataset()
        if not dataset_path:
            logger.error("Failed to download dataset. Exiting.")
            return

        # Load dataset
        df = self.load_dataset(dataset_path)
        if df is None:
            logger.error("Failed to load dataset. Exiting.")
            return

        # Publish to Kafka
        success = self.publish_to_kafka(df)

        # Close producer
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")

        if success:
            logger.info("Dataset successfully published to Kafka!")
        else:
            logger.error("Failed to publish dataset to Kafka")


def main():
    """Main function"""
    producer = SpotifyDatasetProducer()
    producer.run()


if __name__ == "__main__":
    main()
