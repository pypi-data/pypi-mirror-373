"""
Example script for attribute detection with Langvio
"""

import logging
import os

from langvio import create_pipeline

# Load environment variables from .env file (for API keys)

# Set up logging
logging.basicConfig(level=logging.INFO)


def main():
    """Run an attribute detection example"""
    # Create default pipeline
    pipeline = create_pipeline()

    # Create output directory
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    # Example for image attribute detection
    image_path = "data/sample_image.jpeg"  # Replace with your image path

    if os.path.exists(image_path):
        print(f"\n--- Processing image: {image_path} ---")

        # Color attribute query
        query = "Find all red objects in this image"
        print(f"Query: {query}")

        # Process the query
        result = pipeline.process(query, image_path)

        # Display results
        print(f"Output saved to: {result['output_path']}")
        print(f"Explanation: {result['explanation']}")

        # Show detected red objects
        print("\nDetected red objects:")
        for det in result["detections"]["0"]:
            if det.get("attributes", {}).get("color") == "red":
                print(f"- {det['label']} with confidence {det['confidence']:.2f}")

        # Size attribute query
        query = "confirm if a person is wearing yellow or orange in the image ? "
        print(f"\nQuery: {query}")

        # Process the query
        result = pipeline.process(query, image_path)

        # Display results
        print(f"Output saved to: {result['output_path']}")
        print(f"Explanation: {result['explanation']}")

        # Show detected large objects
        print("\nDetected large objects:")
        for det in result["detections"]["0"]:
            if det.get("attributes", {}).get("size") == "large":
                print(f"- {det['label']} with confidence {det['confidence']:.2f}")


if __name__ == "__main__":
    main()
