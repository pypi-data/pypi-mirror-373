# Configuration Guide

Langvio can be configured through YAML files or programmatically to customize models, performance, and output settings.

## Basic Configuration

### Using Different Models

```python
import langvio

# Use specific models
pipeline = langvio.create_pipeline(
    llm_name="gpt-4",           # OpenAI GPT-4
    vision_name="yoloe_large"   # YOLOe large model
)

# Use configuration file
pipeline = langvio.create_pipeline(config_path="my_config.yaml")
```

### Available Models

**Vision Models:**
- `yolo` - YOLO11 nano (fastest, good accuracy)
- `yoloe` - YOLOe small (balanced speed/accuracy)
- `yoloe_medium` - YOLOe medium (better accuracy)
- `yoloe_large` - YOLOe large (best accuracy, slower)

**Language Models:**
- `gpt-3.5` - OpenAI GPT-3.5 Turbo (fast, cost-effective)
- `gpt-4` - OpenAI GPT-4 Turbo (best reasoning)
- `gemini` - Google Gemini Pro (free tier available)

## Configuration File

Create a `config.yaml` file:

```yaml
# Language Model Settings
llm:
  default: "gemini"
  models:
    gemini:
      model_name: "gemini-2.0-flash"
      model_kwargs:
        temperature: 0.2
        max_tokens: 1024
    
    gpt-4:
      model_name: "gpt-4-turbo"
      model_kwargs:
        temperature: 0.1
        max_tokens: 2048

# Vision Model Settings
vision:
  default: "yoloe_large"
  models:
    yoloe_large:
      type: "yolo"
      model_path: "yoloe-11l-seg-pf.pt"
      confidence: 0.5
      model_type: "yoloe"
    
    yolo_fast:
      type: "yolo"
      model_path: "yolo11n.pt"
      confidence: 0.5

# Output Settings
media:
  output_dir: "./output"
  temp_dir: "./temp"
  visualization:
    box_color: [0, 255, 0]      # Green boxes
    text_color: [255, 255, 255]  # White text
    line_thickness: 2
    show_attributes: true
    show_confidence: true

# Logging
logging:
  level: "INFO"
  file: "langvio.log"
```

## Performance Tuning

### For Speed (Real-time Applications)
```python
pipeline = langvio.create_pipeline(
    llm_name="gpt-3.5",      # Faster LLM
    vision_name="yolo"       # Fastest vision model
)
```

### For Accuracy (Research/Analysis)
```python
pipeline = langvio.create_pipeline(
    llm_name="gpt-4",
    vision_name="yoloe_large"
)
```

### For Cost Optimization
```python
pipeline = langvio.create_pipeline(
    llm_name="gemini",       # Google's free tier
    vision_name="yoloe"      # Good balance
)
```

## Video Processing Settings

### Adjust Frame Sampling
```python
# Process every frame (accurate but slow)
result = pipeline.process(query, video_path)

# Or modify in config.yaml
vision:
  models:
    yoloe:
      confidence: 0.3  # Lower = more detections
      sample_rate: 5   # Process every 5th frame
```

### Memory Optimization
```yaml
vision:
  models:
    yolo_efficient:
      model_path: "yolo11n.pt"
      confidence: 0.4
      max_detections: 50  # Limit detections per frame
```

## Output Customization

### Change Visualization Colors
```yaml
media:
  visualization:
    box_color: [255, 0, 0]      # Red boxes
    highlight_color: [0, 0, 255] # Blue for highlighted objects
    text_color: [255, 255, 255]  # White text
    line_thickness: 3
    show_attributes: true
    show_confidence: false       # Hide confidence scores
```

### Custom Output Directory
```python
pipeline = langvio.create_pipeline()
pipeline.config.config["media"]["output_dir"] = "/custom/output/path"
```

## Environment Variables

Set these in your `.env` file or environment:

```env
# Required: LLM API Keys
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# Optional: Performance Settings
CUDA_VISIBLE_DEVICES=0          # Use specific GPU
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Optional: Model Settings
LANGVIO_DEFAULT_LLM=gemini
LANGVIO_DEFAULT_VISION=yoloe
```

## Command Line Usage

```bash
# Basic usage
langvio --query "Count cars" --media parking.jpg

# With custom config
langvio --query "Find red objects" --media scene.jpg --config my_config.yaml

# Specify models
langvio --query "Analyze video" --media traffic.mp4 --llm gpt-4 --vision yoloe_large

# Set output directory
langvio --query "Count people" --media crowd.jpg --output ./results

# List available models
langvio --list-models
```

## Advanced Configuration

### Custom Model Paths
```yaml
vision:
  models:
    custom_yolo:
      model_path: "/path/to/custom/model.pt"
      confidence: 0.3
      device: "cuda"  # or "cpu"
```

### Batch Processing Settings
```python
# For processing multiple files
import os
pipeline = langvio.create_pipeline()

# Process all images in a directory
image_dir = "images/"
for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        result = pipeline.process(
            "What's in this image?", 
            os.path.join(image_dir, filename)
        )
        print(f"{filename}: {result['explanation']}")
```

### Integration with Other Systems
```python
# Use in existing applications
class MyVisionAnalyzer:
    def __init__(self):
        self.pipeline = langvio.create_pipeline(
            config_path="production_config.yaml"
        )
    
    def analyze_security_footage(self, video_path):
        return self.pipeline.process(
            "Detect any unusual activities or security concerns",
            video_path
        )
```

## Configuration Tips

1. **Start with defaults** and adjust based on your needs
2. **Use YOLOe for better accuracy**, YOLO for speed
3. **Gemini is free** for personal use, GPT-4 for best results
4. **Lower confidence values** detect more objects but may have false positives
5. **Increase line thickness** for better visibility in high-resolution images
6. **Disable attributes** for faster processing if not needed