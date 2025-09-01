# Zapdos-Py

A CLI tool for indexing video files by extracting keyframes that can also be used programmatically.

## Installation

To install zapdos-py, you can use pip:

```bash
pip install zapdos-py
```

Or if you're using uv:

```bash
uv pip install zapdos-py
```

## Usage

### Command Line Interface

After installation, you can use the zapdos-py command:

```bash
zapdos-py <video_file_path> [--interval <seconds>]
```

This command will index the specified video file by extracting keyframes at regular intervals.

### Programmatic Usage

You can also use zapdos-py programmatically in your Python code:

```python
from zapdos import index

# Index a video file
try:
    frame_paths = index("path/to/your/video.mp4", interval_sec=30)
    print(f"Extracted {len(frame_paths)} frames")
except FileNotFoundError as e:
    print(f"Error: {e}")
except ValueError as e:
    print(f"Error: {e}")
```

## Example

### CLI Usage
```bash
# Extract frames every 30 seconds (default)
zapdos-py ./video.mp4

# Extract frames every 10 seconds
zapdos-py ./video.mp4 --interval 10
```

### Programmatic Usage
```python
from zapdos import index
from pathlib import Path

# Index a video file
video_path = Path("video.mp4")
try:
    frame_paths = index(video_path, interval_sec=30)
    print(f"Extracted {len(frame_paths)} frames")
    for path in frame_paths:
        print(f"  - {path}")
except FileNotFoundError as e:
    print(f"Error: {e}")
except ValueError as e:
    print(f"Error: {e}")
```

## Supported Video Formats

Zapdos-Py supports the following video formats:
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WMV (.wmv)
- FLV (.flv)
- WEBM (.webm)
- M4V (.m4v)
- 3GP (.3gp, .3g2)
- MPG/MPEG (.mpg, .mpeg, .m2v)

## Development

To set up the project for development:

1. Clone the repository
2. Install uv if you haven't already: `pip install uv`
3. Install the package in development mode:
   ```bash
   uv pip install --editable .
   ```
4. Run the CLI tool:
   ```bash
   zapdos-py <video_file_path>
   ```

## Testing

There are several ways to run the tests:

### Using pytest (recommended):
```bash
pytest tests/
```

### Using unittest directly:
```bash
python -m unittest tests.test_cli
```

### Running the video indexer test:
```bash
python tests/test_video_indexer.py
```

## License

This project is licensed under the MIT License.