#!/usr/bin/env python3
"""
Local test script for Spotify Dataset Kafka Producer
Runs outside Docker for easier testing and debugging
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from producer import SpotifyDatasetProducer


def main():
    """Main function for local testing"""
    # Use localhost for local testing
    local_bootstrap_servers = ["localhost:9092"]

    producer = SpotifyDatasetProducer(
        bootstrap_servers=local_bootstrap_servers, topic="spotify-tracks"
    )

    producer.run()


if __name__ == "__main__":
    main()
