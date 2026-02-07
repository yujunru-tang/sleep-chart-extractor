import argparse
import sys
import os
from PIL import Image
import numpy as np

def extract_sleep_stages_with_rem_above(png_path, grid_spacing_minutes=120, rem_search_height=5):
    """
    Extracts sleep stages from a generated sleep chart image.
    """
    
    # Check file existence to avoid vague PIL errors
    if not os.path.exists(png_path):
        raise FileNotFoundError(f"Image file not found: {png_path}")

    color_stage_map = {
        (255, 255, 0): "N1",
        (0, 128, 0): "N2",
        (0, 128, 128): "N3",
    }
    rem_color = (128, 0, 0)
    wake_stage = "Wake"

    try:
        img = Image.open(png_path).convert("RGB")
    except Exception as e:
        raise RuntimeError(f"Failed to open image: {e}")

    img_arr = np.array(img)
    height, width, _ = img_arr.shape

    # Find gray line y-coord
    gray_mask = np.all(img_arr == [200, 200, 200], axis=2)
    gray_rows = np.where(gray_mask.any(axis=1))[0]
    if len(gray_rows) == 0:
        raise RuntimeError("Gray baseline not found in image")
    base_y = int(np.median(gray_rows))

    # Find leftmost x of gray line (0 min mark)
    gray_cols = np.where(gray_mask[base_y, :])[0]
    if len(gray_cols) == 0:
        raise RuntimeError("No gray pixels found on the scanning line")
    start_x = gray_cols[0]

    # Calculate timeline
    grid_cols = np.where(np.all(img_arr == [128, 128, 128], axis=2).any(axis=0))[0]
    if len(grid_cols) < 2:
        raise RuntimeError("Vertical grid lines not found")
    
    # Calculate scale
    grid_spacing_pixels = grid_cols[1] - grid_cols[0]
    pixels_per_minute = grid_spacing_minutes / grid_spacing_pixels

    stage_seq = []
    first_stage_found = False

    for x in range(start_x, width):
        stage = wake_stage

        # Scan at/below gray line for N1/N2/N3/Wake
        pixel = tuple(img_arr[base_y, x, :])
        if pixel in color_stage_map:
            stage = color_stage_map[pixel]
            first_stage_found = True
        else:
            # Scan `rem_search_height` pixels above line for REM
            for dy in range(1, rem_search_height + 1):
                y_up = base_y - dy
                if y_up < 0:
                    break
                if tuple(img_arr[y_up, x, :]) == rem_color:
                    stage = "REM"
                    first_stage_found = True
                    break
            else:
                # Skip leading Wake stages until the first sleep/data point is found
                if not first_stage_found:
                    continue
                stage = wake_stage

        minute = int(round((x - start_x) * pixels_per_minute))
        stage_seq.append((minute, stage))

    # Merge consecutive identical stages
    compressed_seq = []
    for m, s in stage_seq:
        if not compressed_seq or compressed_seq[-1][1] != s:
            compressed_seq.append((m, s))

    return compressed_seq

if __name__ == "__main__":
    # Setup command line argument parsing
    parser = argparse.ArgumentParser(description="Extract sleep stages from image charts.")
    parser.add_argument("image_path", type=str, help="Path to the input PNG image")
    
    args = parser.parse_args()

    try:
        result = extract_sleep_stages_with_rem_above(args.image_path)
        
        # Output results
        print(f"Processing: {args.image_path}")
        print("-" * 30)
        
        # Print first 50 entries for verification
        for m, s in result[:50]:
            print(f"{m} min: {s}")
            
        if result:
            print("-" * 30)
            print(f"Total Duration: {result[-1][0]} min")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
