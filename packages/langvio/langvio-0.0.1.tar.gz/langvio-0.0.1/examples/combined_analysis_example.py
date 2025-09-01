"""
Example script for combined analysis capabilities with Langvio
"""

import logging
import os

from langvio import create_pipeline

# Load environment variables from .env file (for API keys)

# Set up logging
logging.basicConfig(level=logging.INFO)


def main():
    """Run a comprehensive combined analysis example"""
    # Create default pipeline
    pipeline = create_pipeline()

    # Create output directory
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    # Example for complex image analysis
    image_path = "data/sample_image.jpeg"  # Replace with your image path

    if os.path.exists(image_path):
        print(f"\n--- Comprehensive image analysis: {image_path} ---")

        # Complex analysis combining multiple capabilities
        query = (
            "Analyze this street scene. Count people and vehicles, identify their "
            "locations relative to each other, and note any distinctive colors."
        )
        print(f"Query: {query}")

        # Process the query
        result = pipeline.process(query, image_path)

        # Display results
        print(f"Output saved to: {result['output_path']}")
        print(f"Explanation: {result['explanation']}")

    # Example code for video analysis is commented out since it's not being used
    # but left as reference
    """
    # Example for complex video analysis
    video_path = "examples/data/traffic_video.mp4"  # Replace with your video path

    if os.path.exists(video_path):
        print(f"\n--- Comprehensive video analysis: {video_path} ---")

        # Complex analysis combining multiple capabilities
        query = (
            "Analyze this traffic video. Track vehicles, identify their movement patterns, "
            "count how many pedestrians cross the street, and note any unusual activities."
        )
        print(f"Query: {query}")

        # Process the query
        result = pipeline.process(query, video_path)

        # Display results
        print(f"Output saved to: {result['output_path']}")
        print(f"Explanation: {result['explanation']}")

        # Comprehensive analysis of the results
        print("\nComprehensive video analysis summary:")

        # Count frames and objects
        total_frames = len(result["detections"])

        # Count unique objects by tracking IDs
        tracked_objects = {}
        frame_counts_by_type = defaultdict(int)
        movement_patterns = defaultdict(list)

        for frame_key, detections in result["detections"].items():
            frame_idx = int(frame_key)

            for det in detections:
                frame_counts_by_type[det["label"]] += 1

                # Analyze tracked objects
                if "track_id" in det:
                    track_id = det["track_id"]

                    if track_id not in tracked_objects:
                        tracked_objects[track_id] = {
                            "type": det["label"],
                            "frames": [],
                            "positions": [],
                            "activities": set()
                        }

                    # Record position and frame
                    tracked_objects[track_id]["frames"].append(frame_idx)
                    tracked_objects[track_id]["positions"].append(
                        det["center"] if "center" in det else None
                    )

                    # Record activities
                    for activity in det.get("activities", []):
                        tracked_objects[track_id]["activities"].add(activity)

        # Calculate average objects per frame
        avg_counts = {
            label: count / total_frames for label, count in frame_counts_by_type.items()
        }

        print(f"Total frames analyzed: {total_frames}")
        print(f"Unique tracked objects: {len(tracked_objects)}")

        print("\nAverage objects per frame:")
        for label, avg in sorted(avg_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"- {label}: {avg:.1f}")

        # Analyze movement patterns
        print("\nMovement patterns:")
        activity_summary = defaultdict(lambda: defaultdict(int))

        for track_id, track_data in tracked_objects.items():
            obj_type = track_data["type"]
            for activity in track_data["activities"]:
                activity_summary[obj_type][activity] += 1

        for obj_type, activities in activity_summary.items():
            activities_str = ", ".join([f"{a}:{c}" for a, c in activities.items()])
            print(f"- {obj_type}: {activities_str}")

        # Calculate pedestrian crossings (simplified estimation)
        pedestrians = [data for track_id, data in tracked_objects.items() if data["type"] == "person"]
        crossing_count = sum(1 for ped in pedestrians if len(ped["frames"]) > 10)  # Simple heuristic

        print(f"\nEstimated pedestrian crossings: {crossing_count}")

        # Identify potential unusual events (simplified)
        print("\nPotential unusual events:")

        # Look for stationary vehicles
        stationary_vehicles = []
        for track_id, data in tracked_objects.items():
            if data["type"] in ["car", "truck", "bus"] and "stationary" in data["activities"]:
                duration = len(data["frames"])
                if duration > total_frames * 0.3:  # If stationary for over 30% of video
                    stationary_vehicles.append((track_id, data["type"], duration))

        if stationary_vehicles:
            for track_id, vehicle_type, duration in stationary_vehicles:
                print(f"- Stationary {vehicle_type} (ID {track_id}) for {duration} frames")
        else:
            print("- No unusual events detected")
    """


if __name__ == "__main__":
    main()
