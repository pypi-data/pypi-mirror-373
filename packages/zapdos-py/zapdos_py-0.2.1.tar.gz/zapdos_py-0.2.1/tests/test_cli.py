"""Test module for zapdos video indexing."""

import unittest
from pathlib import Path
from zapdos.cli import index_video_file


class TestZapdos(unittest.TestCase):
    def test_index_video_file_not_exists(self):
        """Test indexing a video file that does not exist."""
        with self.assertRaises(FileNotFoundError):
            index_video_file("nonexistent_video.mp4")


if __name__ == "__main__":
    unittest.main()