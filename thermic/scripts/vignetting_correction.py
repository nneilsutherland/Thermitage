# Import necessary packages
import os
import numpy as np
import glob
import matplotlib.pyplot as plt
from PIL import Image
from scipy.interpolate import griddata
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
import argparse

def vignetting_correction(input_folder, output_folder, start_time, end_time, target_format):
      # Create the output folder if it doesn't exist:
      if not os.path.exists(output_folder):
            os.makedirs(output_folder)

      
      # Get a list of all image files in the input folder:
      image_files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))]
      print("Number of files loaded:", len(image_files))

      # Access Folder:
      tiff_files = glob.glob(os.path.join(input_folder, "*.tiff"))
      print(f"Found {len(tiff_files)} TIFF files")

      # Assess No. of Images:
      if len(tiff_files) == 0:
            print("ERROR: No TIFF files found! Check your folder path.")
      else:
            print("Sample files found:")
      for i, file in enumerate(tiff_files[:3]):  # Show first 3 files
            print(f"{i+1}. {os.path.basename(file)}")
      if len(tiff_files) > 5:
            print(f"... and {len(tiff_files) - 5} more files")

      # Check First 3 Files: 
      sample_files = tiff_files[:3]  
      print("Checking image dimensions:")
      for i, file_path in enumerate(sample_files):
            try:
                  with Image.open(file_path) as img:
                        filename = os.path.basename(file_path)
                        width, height = img.size
                        print(f"{i+1}. {filename}: {width}x{height} pixels")
            except Exception as e:
                  print(f"Error reading {file_path}: {str(e)}")
      
      file_paths = []
timestamps = []
absolute_seconds = []

# Parse timestamps from filenames
for file_path in tiff_files:
    filename = os.path.basename(file_path)
    timestamp_raw = filename.replace('-radiometric.tiff', '')
    time_parts = timestamp_raw.split('-')

    if len(time_parts) >= 4:
        try:
            h, m, s, ms = map(int, time_parts[:4])
            total_sec = h * 3600 + m * 60 + s + ms / 1000
            timestamp_str = f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
            file_paths.append(file_path)
            timestamps.append(timestamp_str)
            absolute_seconds.append(total_sec)
        except ValueError:
            file_paths.append(file_path)
            timestamps.append("Invalid")
            absolute_seconds.append(None)
    else:
        file_paths.append(file_path)
        timestamps.append("Invalid")
        absolute_seconds.append(None)

      # Compute elapsed times from first valid timestamp
      valid_times = [t for t in absolute_seconds if t is not None]
      if valid_times:
      first_time = min(valid_times)
      elapsed_seconds = [
            int(t - first_time) if t is not None else None for t in absolute_seconds
      ]
      elapsed_timestr = [
            f"{int(t // 3600):02d}:{int((t % 3600) // 60):02d}:{int(t % 60):02d}"
            if t is not None else "Invalid"
            for t in elapsed_seconds
      ]
      else:
      elapsed_seconds = [None] * len(file_paths)
      elapsed_timestr = ["Invalid"] * len(file_paths)

      df = pd.DataFrame({
      "file_path": file_paths,
      "timestamp_OBJ": timestamps,
      "absolute_seconds": absolute_seconds,
      "elapsed_seconds": elapsed_seconds,
      "timestamp_STR": elapsed_timestr,
      })

      df = df.sort_values(by='elapsed_seconds', ascending=True).reset_index(drop=True)
      print(f"DataFrame created with shape: {df.shape}")
      print(f"Columns: {list(df.columns)}")

      df.head(15)
    
    def vignetting_image(tiff_files, elapsed_timestamps, start_time_str, end_time_str):
    """
    Load and average the WWP 16-bit images within a given time range, then return
    the vignetting map (temperature deviation from central pixel).
    
    Returns:
        vignetting_map: 2D array of temperature deviation (in °C).
    """
    # Look up elapsed_seconds from timestamp_STR
    start_matches = df.loc[df["timestamp_STR"] == start_time_str, "elapsed_seconds"]
    end_matches = df.loc[df["timestamp_STR"] == end_time_str, "elapsed_seconds"]

    if start_matches.empty or end_matches.empty:
        raise ValueError("Start or end timestamp_STR not found in DataFrame.")

    start_sec = start_matches.iloc[0]
    end_sec = end_matches.iloc[0]

    # Select files within time range
    selected_files = [
        f for f, ts in zip(tiff_files, elapsed_timestamps)
        if ts is not None and start_sec <= ts <= end_sec
        ]

    if not selected_files:
        raise ValueError("No images found in the given time range.")

    print(f"Averaging {len(selected_files)} 16-bit thermal images from {start_time_str} to {end_time_str}")

      # Load and stack images
      image_stack = []
      for file_path in selected_files:
            img = Image.open(file_path)
            img_array = np.array(img, dtype=np.float32)
            image_stack.append(img_array)

      image_stack = np.stack(image_stack, axis=0)
      mean_dn = np.mean(image_stack, axis=0)

      # Convert to temperature in °C
      temperature_map = (mean_dn / 40.0) - 100.0

      # Subtract central pixel to get vignetting map
      h, w = temperature_map.shape
      center_value = temperature_map[h // 2, w // 2]
      vignetting_map = temperature_map - center_value

      return vignetting_map

      print("Process Completed")

if __name__ == "__main__":
      # Parse command-line arguments
      parser = argparse.ArgumentParser(description="Enhance images in a folder to a target image format using OpenCV and ImageJ.")
      parser.add_argument("--input_folder", type=str, help="Path to the folder containing input images.")
      parser.add_argument("--output_folder",type=str, help="Path to the folder where enhanced images will be saved. If not provided, it will be created within the input folder.")
      parser.add_argument("--target_format", type=str, help="Desired Vignetting COrrection Image format (e.g., ).")
      args = parser.parse_args()

    # Call the enhance_images function with provided arguments
      vignetting_correction(args.input_folder, args.output_folder, args.start_time, args.end_time, args.target_format)
