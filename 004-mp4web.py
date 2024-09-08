import cv2
import tkinter as tk
from tkinter import filedialog
import os
from tqdm import tqdm

def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select a video file", filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
    return file_path

def crop_center_square(frame):
    height, width = frame.shape[:2]
    min_dim = min(width, height)
    start_x = (width - min_dim) // 2
    start_y = (height - min_dim) // 2
    return frame[start_y:start_y+min_dim, start_x:start_x+min_dim]

def scale_to_1080p(frame, original_resolution):
    if original_resolution == (1920, 1080):
        return frame  # Already 1080p
    elif original_resolution == (1280, 720):
        return cv2.resize(frame, (1920, 1080))  # Upscale to 1080p
    elif original_resolution == (3840, 2160):
        return cv2.resize(frame, (1920, 1080))  # Downscale to 1080p
    else:
        raise ValueError(f"Unexpected resolution: {original_resolution}")

def process_video(input_path, output_path, target_duration=60):
    cap = cv2.VideoCapture(input_path)
    
    # Get video properties
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    original_resolution = (original_width, original_height)
    original_duration = frame_count / fps
    frames_to_skip = max(1, int(original_duration / target_duration))

    # Create VideoWriter object to save the new video
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec, ensures web compatibility
    out = cv2.VideoWriter(output_path, fourcc, fps, (1080, 1080))

    current_frame = 0
    processed_frames = 0

    print(f"Original Resolution: {original_resolution}")
    print(f"Original Duration: {original_duration:.2f} seconds")
    print(f"Target Duration: {target_duration} seconds")
    print(f"Frame count: {frame_count}, FPS: {fps}, Frames to skip: {frames_to_skip}")

    total_frames = frame_count // frames_to_skip
    update_interval = total_frames // 20  # 5% intervals

    with tqdm(total=total_frames) as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if current_frame % frames_to_skip == 0:
                # Scale to 1080p if needed
                scaled_frame = scale_to_1080p(frame, original_resolution)
                # Crop to center square
                cropped_frame = crop_center_square(scaled_frame)
                resized_frame = cv2.resize(cropped_frame, (1080, 1080))
                out.write(resized_frame)
                processed_frames += 1

                # Update progress bar every 5% of total progress
                if processed_frames % update_interval == 0:
                    pbar.update(update_interval)
            
            current_frame += 1

        # Final update to ensure the progress bar completes
        if processed_frames % update_interval != 0:
            pbar.update(total_frames - pbar.n)

    cap.release()
    out.release()

if __name__ == "__main__":
    video_file = select_file()
    if not video_file:
        print("No file selected, exiting.")
    else:
        output_file = os.path.splitext(video_file)[0] + '_timelapse.mp4'
        process_video(video_file, output_file)
        print(f"Timelapse video saved as {output_file}")
