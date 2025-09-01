"""
Example script for counting objects with Langvio
"""

import logging
import os

from langvio import create_pipeline

# Set up logging
logging.basicConfig(level=logging.INFO)


def main():
    """Run an object counting example"""
    # Create default pipeline
    pipeline = create_pipeline()

    # Create output directory
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    # Example for image counting
    image_path = "data/sample_image.jpeg"  # Replace with your image path

    if os.path.exists(image_path):
        print(f"\n--- Processing image: {image_path} ---")

        # Counting query
        query = "Count how many people are in this image"
        print(f"Query: {query}")

        # Process the query
        result = pipeline.process(query, image_path)

        # Display results
        print(f"Output saved to: {result['output_path']}")
        print(f"Explanation: {result['explanation']}")

    # # Example for video counting
    # video_path = "data/traffic_video.mp4"  # Replace with your video path
    #
    # if os.path.exists(video_path):
    #     print(f"\n--- Processing video: {video_path} ---")
    #
    #     # Counting query
    #     query = "Count the number of vehicles in this video"
    #     print(f"Query: {query}")
    #
    #     # Process the query
    #     result = pipeline.process(query, video_path)
    #
    #     # Display results
    #     print(f"Output saved to: {result['output_path']}")
    #     print(f"Explanation: {result['explanation']}")
    #
    #     # Count vehicles manually to verify
    #     vehicle_classes = ["car", "truck", "bus", "motorcycle", "bicycle"]
    #     vehicle_counter = Counter()
    #
    #     for frame_key, detections in result["detections"].items():
    #         for det in detections:
    #             if det["label"] in vehicle_classes:
    #                 vehicle_counter[det["label"]] += 1
    #
    #     print("Verified vehicle counts per frame:")
    #     for vehicle, count in vehicle_counter.items():
    #         print(f"- {vehicle}: {count}")


if __name__ == "__main__":
    main()
