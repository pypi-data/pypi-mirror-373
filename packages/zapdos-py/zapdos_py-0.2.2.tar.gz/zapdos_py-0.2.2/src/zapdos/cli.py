"""CLI module for zapdos video indexing."""

import argparse
import sys
from pathlib import Path
from typing import Union
from .video_indexer import index


def index_video_file(file_path: Union[str, Path], interval: int = 30) -> bool:
    """Index the specified video file by extracting keyframes.
    
    Args:
        file_path: Path to the video file to index
        interval: Interval between frames in seconds (default: 30)
        
    Returns:
        bool: True if indexing was successful, False otherwise
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    if not path.exists():
        raise FileNotFoundError(f"Video file '{file_path}' does not exist.")
    
    try:
        print(f"Indexing video file: {path.absolute()}")
        frame_paths = index(path, interval_sec=interval)
        print(f"Extracted {len(frame_paths)} frames")
        # In a real implementation, this is where you would upload to S3
        print("Video indexing completed successfully")
        return True
    except Exception as e:
        print(f"Error indexing video file: {e}")
        return False


def main() -> None:
    """Main entry point for the zapdos CLI."""
    parser = argparse.ArgumentParser(
        description="Zapdos - A CLI tool for indexing video files"
    )
    parser.add_argument(
        "file_path", 
        help="Path to the video file to index"
    )
    parser.add_argument(
        "--interval", 
        type=int, 
        default=30,
        help="Interval between frames in seconds (default: 30)"
    )
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Handle video indexing
    try:
        index_video_file(args.file_path, args.interval)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()