import cv2
import os
from pathlib import Path
import numpy as np
import yt_dlp

def process_local_video(video_path, output_dir, sample_rate=30, target_size=(212, 212)):
    """
    Process a local video file (like .mov)
    Args:
        video_path: Path to local video file
        output_dir: Directory to save extracted frames
        sample_rate: Extract every Nth frame
        target_size: Target size for frame resizing
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    # Create output directory
    frames_dir = os.path.join(output_dir, 'frames')
    Path(frames_dir).mkdir(parents=True, exist_ok=True)
    
    # Extract frames
    print(f"Extracting frames from: {video_path}")
    num_frames = extract_frames(video_path, frames_dir, sample_rate, target_size)
    print(f"Extracted {num_frames} frames to {frames_dir}")
    
    return num_frames

def download_youtube_video(url, output_path):
    """Download YouTube video using yt-dlp"""
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s')
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return os.path.join(output_path, f"{info['title']}.mp4")

def resize_image(image, target_size=(212, 212)):
    """Resize image to target size while maintaining aspect ratio"""
    return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

def extract_frames(video_path, output_dir, sample_rate=30, target_size=(212, 212)):
    """Extract frames from video at given sample rate and resize them"""
    cap = cv2.VideoCapture(video_path)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    frame_count = 0
    saved_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % sample_rate == 0:
            # Resize frame
            resized_frame = resize_image(frame, target_size)
            
            # Save frame as PNG
            output_path = os.path.join(output_dir, f'frame_{saved_count:05d}.png')
            cv2.imwrite(output_path, resized_frame)
            saved_count += 1
            
        frame_count += 1
        
    cap.release()
    return saved_count

def process_videos(video_urls, base_output_dir, target_size=(212, 212)):
    """Process multiple YouTube videos"""
    for i, url in enumerate(video_urls):
        try:
            # Create output directory for this video
            video_dir = os.path.join(base_output_dir, f'video_{i:02d}')
            Path(video_dir).mkdir(parents=True, exist_ok=True)
            
            # Download video
            print(f"Downloading video {i+1}/{len(video_urls)}: {url}")
            video_path = download_youtube_video(url, video_dir)
            
            # Extract frames
            print(f"Extracting frames from video {i+1}")
            frames_dir = os.path.join(video_dir, 'frames')
            num_frames = extract_frames(video_path, frames_dir, sample_rate=30, target_size=target_size)
            print(f"Extracted {num_frames} frames")
            
            # Clean up downloaded video
            os.remove(video_path)
            
        except Exception as e:
            print(f"Error processing video {url}: {str(e)}")
            continue

# Example usage for local .mov file
local_video_path = "Data preparation/drones3.mov"  # Replace with your .mov file path
output_directory = 'suas_dataset'
target_size = (224, 224)

# Process local video
try:
    num_frames = process_local_video(
        video_path=local_video_path,
        output_dir=output_directory,
        sample_rate=3,  # Extract every 30th frame, adjust as needed
        target_size=target_size
    )
except Exception as e:
    print(f"Error processing local video: {str(e)}")

# If you still want to process YouTube videos, you can use:
# video_urls = ['https://www.youtube.com/watch?v=example']
# process_videos(video_urls, output_directory, target_size)