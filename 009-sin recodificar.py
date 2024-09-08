import cv2
import tkinter as tk
from tkinter import filedialog
import os
from tqdm import tqdm

def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select a folder containing video files")
    return folder_path

def crop_center_square(frame):
    height, width = frame.shape[:2]
    min_dim = min(width, height)
    start_x = (width - min_dim) // 2
    start_y = (height - min_dim) // 2
    return frame[start_y:start_y+min_dim, start_x:start_x+min_dim]

def crop_center_vertical(frame):
    height, width = frame.shape[:2]
    new_width = height * 9 // 16  # Maintain aspect ratio for 1080x1920
    start_x = (width - new_width) // 2
    return frame[:, start_x:start_x+new_width]

def process_video(input_path, output_folder, target_duration=60):
    cap = cv2.VideoCapture(input_path)
    
    # Get video properties
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    original_resolution = (original_width, original_height)
    original_duration = frame_count / fps
    frames_to_skip = max(1, int(original_duration / target_duration))

    # Define output filenames
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    instagram_output = os.path.join(output_folder, f"{base_name}_instagram_timelapse.mp4")
    tiktok_output = os.path.join(output_folder, f"{base_name}_tiktok_timelapse.mp4")
    youtube_output = os.path.join(output_folder, f"{base_name}_youtube_timelapse.mp4")

    # Create VideoWriter objects for Instagram, TikTok, and YouTube videos
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec, ensures web compatibility
    out_instagram = cv2.VideoWriter(instagram_output, fourcc, fps, (1080, 1080))
    out_tiktok = cv2.VideoWriter(tiktok_output, fourcc, fps, (1080, 1920))
    out_youtube = cv2.VideoWriter(youtube_output, fourcc, fps, original_resolution)

    current_frame = 0
    processed_frames = 0

    print(f"Processing {input_path}...")
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
                # Scale to 1080p if needed for Instagram and TikTok
                scaled_frame = cv2.resize(frame, (1920, 1080)) if original_resolution != (1920, 1080) else frame
                
                # Process Instagram video (1080x1080)
                cropped_square = crop_center_square(scaled_frame)
                resized_square = cv2.resize(cropped_square, (1080, 1080))
                out_instagram.write(resized_square)

                # Process TikTok video (1080x1920)
                cropped_vertical = crop_center_vertical(scaled_frame)
                resized_vertical = cv2.resize(cropped_vertical, (1080, 1920))
                out_tiktok.write(resized_vertical)

                # Process YouTube video (original resolution)
                out_youtube.write(frame)  # Use the original frame without resizing

                processed_frames += 1

                # Update progress bar every 5% of total progress
                if processed_frames % update_interval == 0:
                    pbar.update(update_interval)
            
            current_frame += 1

        # Final update to ensure the progress bar completes
        if processed_frames % update_interval != 0:
            pbar.update(total_frames - pbar.n)

    cap.release()
    out_instagram.release()
    out_tiktok.release()
    out_youtube.release()

def process_folder():
    folder_path = select_folder()
    if not folder_path:
        print("No folder selected, exiting.")
        return

    output_folder = os.path.join(folder_path, "redes")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(folder_path):
        if file_name.endswith((".mp4", ".avi", ".mov")):
            file_path = os.path.join(folder_path, file_name)
            process_video(file_path, output_folder)
    
    print(f"All videos processed and saved in {output_folder}")

if __name__ == "__main__":
    process_folder()
