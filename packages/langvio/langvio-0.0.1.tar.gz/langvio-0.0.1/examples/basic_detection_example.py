"""
Example script for basic object detection with Langvio
"""

import logging
import os

from langvio import create_pipeline

# Set up logging
logging.basicConfig(level=logging.INFO)


def main():
    """Run a basic object detection example"""
    # Create default pipeline
    pipeline = create_pipeline()

    # Create output directory
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    # Example for image detection
    image_path = "data/sample_image.jpeg"  # Replace with your image path

    if os.path.exists(image_path):
        print(f"\n--- Processing image: {image_path} ---")

        # Basic detection query
        query = "What objects are in this image?"
        print(f"Query: {query}")

        # Process the query
        result = pipeline.process(query, image_path)

        # Display results
        print(f"Output saved to: {result['output_path']}")
        print(f"Explanation: {result['explanation']}")
        # print("\nDetected objects:")
        #


if __name__ == "__main__":
    main()
