"""Video indexing module for zapdos."""

import os
import tempfile
import av
import cv2
import aiofiles
import queue
import threading
import asyncio
from pathlib import Path
from multiprocessing import cpu_count, get_context
from typing import List, Union


def _encode_frame(frame: av.VideoFrame) -> bytes | None:
    """Encode a video frame to JPEG bytes."""
    try:
        img_bgr = frame.to_ndarray(format="bgr24")
        # Use even lower quality for faster encoding (we only need visual reference)
        success, buf = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
        if not success:
            return None
        return buf.tobytes()
    except Exception as ex:
        print(f"[encode] error: {ex}")
        return None


async def _write_file_async(path: str, data: bytes) -> None:
    """Asynchronously write data to a file."""
    try:
        async with aiofiles.open(path, "wb") as f:
            await f.write(data)
    except Exception as ex:
        print(f"[write] error {path}: {ex}")


def _background_writer(task_queue: queue.Queue, stop_event: threading.Event):
    """Background thread that greedily consumes write tasks from the queue."""
    
    async def _process_queue():
        """Process tasks from the queue asynchronously."""
        while not stop_event.is_set() or not task_queue.empty():
            try:
                # Try to get a task from the queue with a timeout
                coro = task_queue.get_nowait()
                await coro
                task_queue.task_done()
            except queue.Empty:
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.001)
            except Exception as ex:
                print(f"[background writer] error: {ex}")
    
    # Run the async processing loop
    asyncio.run(_process_queue())


def _process_chunk(args):
    """
    Worker: for each timestamp, seek, decode ONE frame, encode to JPEG.
    Tasks are added to a queue and consumed by a background writer.
    """
    video_path, timestamps, output_dir, chunk_id = args
    output_dir = str(output_dir)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    container = None
    
    # Queue for write tasks
    task_queue = queue.Queue()
    
    # Start background writer thread
    stop_event = threading.Event()
    writer_thread = threading.Thread(target=_background_writer, 
                                   args=(task_queue, stop_event), 
                                   daemon=True)
    writer_thread.start()
    
    try:
        container = av.open(str(video_path))
        stream = container.streams.video[0]
        tb = float(stream.time_base)

        for i, target_ts_ms in enumerate(timestamps):
            try:
                seek_pts = int((target_ts_ms / 1000.0) / tb)
                container.seek(seek_pts, any_frame=False, backward=True, stream=stream)

                frame = next(container.decode(stream), None)
                if frame is None:
                    continue

                frame_time_ms = int(frame.pts * tb * 1000) if frame.pts else target_ts_ms
                
                filename_ts = f"{frame_time_ms:011d}ms"
                filename = f"keyframe_{filename_ts}_chunk{chunk_id}_i{i}.jpg"
                out_path = os.path.join(output_dir, filename)

                # Create the write coroutine and add it to the queue
                encoded_data = _encode_frame(frame)
                if encoded_data is not None:
                    coro = _write_file_async(out_path, encoded_data)
                    task_queue.put(coro)

            except Exception as ex:
                print(f"[chunk {chunk_id}] Error at {target_ts_ms}ms: {ex}")

        # Wait for all tasks to be processed
        task_queue.join()

    finally:
        # Signal the background writer to stop
        stop_event.set()
        writer_thread.join(timeout=5)  # Wait up to 5 seconds for writer to finish
        
        if container:
            try:
                container.close()
            except Exception:
                pass


def extract_keyframes(video_path: Union[str, Path], output_dir: Union[str, Path], 
                     interval_sec: int = 30, workers: int = None) -> List[str]:
    """
    Extract frames at regular intervals from a video using PyAV + multiprocessing.
    
    Args:
        video_path: Path to the video file
        output_dir: Directory to save extracted frames
        interval_sec: Interval between frames in seconds
        workers: Number of worker processes to use
        
    Returns:
        List of paths to extracted frame files
    """
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get video duration
    container = av.open(str(video_path))
    stream = container.streams.video[0]
    duration_ms = float(stream.duration * stream.time_base * 1000)
    container.close()

    timestamps = list(range(0, int(duration_ms), interval_sec * 1000))
    print(f"Extracting {len(timestamps)} frames at {interval_sec}s intervals")

    if workers is None:
        workers = max(1, min(cpu_count() - 1, 4))

    # Split timestamps into continuous chunks for workers
    # Each worker gets a continuous range of timestamps
    chunks = []
    total_timestamps = len(timestamps)
    
    # Calculate chunk boundaries to ensure continuity
    for i in range(workers):
        start_idx = i * total_timestamps // workers
        end_idx = (i + 1) * total_timestamps // workers
        chunk = timestamps[start_idx:end_idx]
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
    
    args = [(video_path, chunk, output_dir, idx) for idx, chunk in enumerate(chunks)]

    ctx = get_context("fork")  # force fork to avoid spawn overhead
    with ctx.Pool(workers) as pool:
        pool.map(_process_chunk, args)  # no return values needed

    print(f"Frames extraction completed to '{output_dir}'")
    
    # Return list of extracted frame paths
    return list(str(p) for p in output_dir.glob("*.jpg"))


def index(video_path: Union[str, Path], interval_sec: int = 30) -> List[str]:
    """
    Index a video file by extracting keyframes at regular intervals.
    
    This function receives a video file, checks if it has a valid video extension,
    runs random access to get a list of images in a temporary folder, and returns
    the paths to the extracted frames.
    
    Args:
        video_path: Path to the video file to index
        interval_sec: Interval between frames in seconds (default: 30)
        
    Returns:
        List of paths to extracted frame files
        
    Raises:
        FileNotFoundError: If the video file does not exist
        ValueError: If the file is not a valid video file
    """
    # Check if file exists
    path = Path(video_path) if isinstance(video_path, str) else video_path
    if not path.exists():
        raise FileNotFoundError(f"Video file '{video_path}' does not exist.")
    
    # Check if file has a valid video extension
    valid_extensions = {
        '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', 
        '.m4v', '.3gp', '.3g2', '.mpg', '.mpeg', '.m2v', '.m4v'
    }
    
    if path.suffix.lower() not in valid_extensions:
        raise ValueError(f"File '{video_path}' is not a valid video file. "
                         f"Supported extensions: {', '.join(valid_extensions)}")
    
    # Create a temporary directory for extracted frames
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "keyframes"
        
        # Extract keyframes
        frame_paths = extract_keyframes(
            video_path=path,
            output_dir=output_dir,
            interval_sec=interval_sec
        )
        
        # Move frames to a more permanent location
        # In a real implementation, this is where you would upload to S3
        # For now, we'll just return the paths
        return frame_paths