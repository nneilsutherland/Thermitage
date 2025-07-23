import os
import numpy as np
from PIL import Image, ExifTags
import argparse
import pandas as pd
from datetime import datetime
import exifread
import warnings

"""
Script for generating a Vignetting Correction Image from calibration-like thermal images. 
Further details on proper set-up and execution for the generation of suitable data can be found in: 
'docs/vignetting_correction.md'. 

This script reads a sequence of thermal images (TIFF or JPEG) from a specified folder,
extracts their capture timestamps from EXIF metadata, and computes a vignetting correction
image by averaging the image stack over a specified time window.

Features:
- Supports TIFF (.tif, .tiff) and JPEG (.jpg, .jpeg) formats with valid EXIF data.
- Extracts 'DateTimeOriginal' from image metadata to determine image timing. Original images are required 
or alternative timestamps can be integrated into the code (e.g., filename splitting if suitable).)
- Allows optional specification of start and/or end time (relative to the first image). If no start or end times 
are provided, the entire set of images will be averaged.
- Preserves 16-bit image in the output to retain digital number values (representative of temperature).

Usage:
  python vignetting_correction.py --input_folder /path/to/images [--start_time HH:MM:SS] [--end_time HH:MM:SS]

Arguments:
  --input_folder   Required. Path to the folder containing calibration images.
  --start_time     Optional. Start time (HH:MM:SS) relative to the first image timestamp.
  --end_time       Optional. End time (HH:MM:SS) relative to the first image timestamp.

Example:
  python vignetting_correction.py --input_folder ./data/calibration_set --start_time 00:00:00 --end_time 00:02:00
"""

# Extract Date/Time from EXIF data (file format dependent):
def extract_exif_timestamp(image_path):
      ext = os.path.splitext(image_path)[1].lower()
     
      # === JPEG and JPG ===
      if ext in ['.jpg', '.jpeg', '.JPG']:
            try:
                  with Image.open(image_path) as img:
                        exif = img._getexif() # type: ignore
                        if exif:
                              for tag, value in exif.items():
                                    decoded = ExifTags.TAGS.get(tag, tag)
                                    if decoded == 'DateTimeOriginal':
                                          return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
            except Exception as e:
                  print(f"[WARNING] JPG or JPEG EXIF read failed for {os.path.basename(image_path)}: {e}")

      # === TIFF ===
      elif ext in ['.tif', '.tiff']:
            try:
                  with open(image_path, 'rb') as f:
                        tags = exifread.process_file(f, stop_tag='Image DateTimeOriginal')
                        for tag in tags.keys():
                              if tag == 'Image DateTimeOriginal':
                                    dt_str = str(tags[tag])
                                    return datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
            except Exception as e:
                  print(f"[WARNING] TIFF EXIF read failed for {image_path}: {e}")

      else:
            print(f"[INFO] Unsupported or unhandled format for EXIF extraction: {image_path}")

      return None

# Create DataFrame with Files and Timestamps:
def load_images_with_timestamps(input_folder):
      supported_exts = ('.tif', '.tiff', '.jpg', '.jpeg', '.JPG', '.png')
      image_data = []

      print(f"[INFO] Scanning folder: {input_folder}")
      for filename in os.listdir(input_folder):
            if filename.lower().endswith(supported_exts):
                  full_path = os.path.join(input_folder, filename)
                  timestamp = extract_exif_timestamp(full_path)
                  if timestamp:
                        image_data.append((full_path, timestamp))
                  else:
                        print(f"[WARNING] No EXIF timestamp for {filename}")

      df = pd.DataFrame(image_data, columns=['file_path', 'timestamp'])
      df.sort_values(by='timestamp', inplace=True)
      df.reset_index(drop=True, inplace=True)

      print(f"[INFO] Loaded {len(df)} valid images with EXIF timestamps.")
      return df

# Filter calibration images based on start and end times (HH:MM:SS):
def filter_images_by_time(df, start_time=None, end_time=None):
      base_time = df['timestamp'].iloc[0]  # Timestamp of the first image
      df['elapsed'] = df['timestamp'].apply(lambda t: (t - base_time).total_seconds())

      # If no times are given, use all images:
      if not start_time and not end_time:
            print(f"[INFO] No time filtering applied. Using all {len(df)} images.")
            return df

      # If only end_time is given — invalid
      if not start_time and end_time:
            raise ValueError("Cannot specify end_time without start_time.")

      # Convert elapsed thresholds
      start_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], start_time.split(":"))) if start_time else 0
      end_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], end_time.split(":"))) if end_time else float('inf')

      filtered = df[(df['elapsed'] >= start_seconds) & (df['elapsed'] <= end_seconds)]
      print(f"[INFO] Selected {len(filtered)} images from {start_time or '00:00:00'} to {end_time or 'end'} (elapsed)")
      return filtered

# Compute Vignetting Correction Image (Averaged Image):
def compute_vignetting_average(image_paths):
      image_stack = []

      for path in image_paths:
            try:
                  with Image.open(path) as img:
                        img_array = np.array(img, dtype=np.float32)
                        image_stack.append(img_array)
      
            except Exception as e:
                  print(f"[ERROR] Skipping {path}: {e}")

      if not image_stack:
            raise ValueError("No valid images to process.")

      stacked = np.stack(image_stack)
      mean_image = np.mean(stacked, axis=0)
      print(f"[INFO] {len(image_stack)} images averaged successfully.")
      
      return mean_image

# Save Vignetting COrrection image in 16-bit .tiff (to preserve temperature / digital numbers):
def save_output_image(mean_array, output_path):

      warnings.filterwarnings("ignore", category=DeprecationWarning) # Removing Pillow 13 Deprecation Error message (Image.fromarray)
     
      try:
            result_image = Image.fromarray(mean_array.astype(np.uint16), mode='I;16')
            result_image.save(output_path)
            print(f"[SUCCESS] Saved 16-bit TIFF image to: {output_path}")
      except Exception as e:
            print(f"[ERROR] Could not save image: {e}")

# Complete Vignetting Correction Image Function:
def vignetting_correction(input_folder, start_time=None, end_time=None):
      df = load_images_with_timestamps(input_folder)
      filtered_df = filter_images_by_time(df, start_time, end_time)

      if filtered_df.empty:
            print("[ERROR] No images found in the specified time range.")
            return

      mean_array = compute_vignetting_average(filtered_df['file_path'].tolist())

      if start_time and end_time:
            suffix = f"{start_time.replace(':', '')}_to_{end_time.replace(':', '')}"
      elif start_time:
            suffix = f"{start_time.replace(':', '')}_to_END"
      else:
            suffix = "ALL"

      output_filename = f"VignCorrImg_{suffix}.tiff"
      output_path = os.path.join(input_folder, output_filename)
      save_output_image(mean_array, output_path)

if __name__ == "__main__":
     parser = argparse.ArgumentParser(description="Compute a vignetting correction image from a folder of thermal images.")
     parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing input images.")
     parser.add_argument("--start_time", type=str, help="Start time (format: 'HH:MM:SS' from first image).")
     parser.add_argument("--end_time", type=str, help="End time (format: 'HH:MM:SS' from first image).")
     
     args = parser.parse_args()
     vignetting_correction(args.input_folder, args.start_time, args.end_time)

    # - - - - - - - - - - - COMMENTS - - - - - - - - - - -

    # Currently not working for DJI_M3T as EXIF data is missing!!!
    # Also need to find a way of generating for 8-bit