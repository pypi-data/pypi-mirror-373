

import os
import subprocess
from simba.utils.read_write import get_video_meta_data

def create_video_mosaic(input_dir, output_file, rows, cols):
    # First input is used to get resolution
    sample_file = os.path.join(input_dir, f"tile_0_0.mp4")
    vid_w, vid_h = get_video_meta_data(sample_file)['width'], get_video_meta_data(sample_file)['height']

    inputs = []
    filter_inputs = []
    layout_parts = []
    idx = 0

    for row in range(rows):
        for col in range(cols):
            filename = os.path.join(input_dir, f"tile_{row}_{col}.mp4")
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Missing file: {filename}")
            inputs += ['-i', filename]
            filter_inputs.append(f"[{idx}:v]")
            layout_parts.append(f"{col * vid_w}_{row * vid_h}")
            idx += 1

    filter_complex = f"{''.join(filter_inputs)}xstack=inputs={rows * cols}:layout=" + "|".join(layout_parts) + "[v]"

    cmd = [
        'ffmpeg',
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '[v]',
        '-c:v', 'libx264',
        '-crf', '23',
        '-preset', 'fast',
        output_file
    ]

    print("Running FFmpeg command:")
    print(' '.join(cmd))

    subprocess.run(cmd, check=True)

# Example usage:
create_video_mosaic(input_dir=r"D:\troubleshooting\netholabs\original_videos\1_tiles\original\out_videos", output_file=r"D:\troubleshooting\netholabs\original_videos\1_tiles\original\out_videos\saved\mosaic_3.mp4", rows=3, cols=6)
