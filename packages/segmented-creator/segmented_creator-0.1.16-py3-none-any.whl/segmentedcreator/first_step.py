import cv2
import os
import segmentedcreator.tooldata as td
from tqdm import tqdm
import argparse
import yaml

def parse_arguments(config_path="config.yaml"):
    parser = argparse.ArgumentParser(description="Video processing")
    parser.add_argument("--root", type=str, default=None, help="Path to the video file")
    parser.add_argument("--fac", type=int, help="Scaling factor for resizing images")
    parser.add_argument("--model_cfg", type=str, default="configs/sam2.1/sam2.1_hiera_l.yaml", help="Path to the SAM2 model configuration file")
    parser.add_argument("--sam2_chkpt", type=str, default=None, help="Path to the SAM2 model checkpoint file")
    parser.add_argument("--n_imgs", type=int, default=100, help="Number of images to process per batch")
    parser.add_argument("--n_obj", type=int, default=20, help="Number of objects to process per batch")
    parser.add_argument("--img_size_sahi", type=int, default=512, help="Image size for the SAHI model")
    parser.add_argument("--overlap_sahi", type=float, default=0.2, help="Overlap threshold for SAHI detections")

    args = parser.parse_args()

    # Load previous config, if it exists
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        # Fill in any unspecified CLI arguments
        for key, value in config_data.items():
            if getattr(args, key) is None:
                setattr(args, key, value)

    return args

def guardar_configuracion(args, config_path="config.yaml"):
    # Load current config if exists
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
    else:
        config_data = {}

    # Update with current values
    config_data.update({k: v for k, v in vars(args).items() if v is not None})

    with open(config_path, "w") as f:
        yaml.dump(config_data, f)

def procesar_video(folders):
    # Capture video
    cap = cv2.VideoCapture(folders["video_path"])
    frame_count = 0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    progress = tqdm(total=total_frames, desc="Processing frames", unit="frame")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count == 0:
            # Save the first frame as reference
            frame0 = frame.copy()

        frame = td.alinear_imagen(frame0, frame)

        # Image file name
        frame_filename = os.path.join(folders["imgs_folder_A"], f'{frame_count:05d}.jpg')

        # Save the frame as a JPEG image
        cv2.imwrite(frame_filename, frame)
        frame_count += 1
        progress.update(1)

    cap.release()
    progress.close()
    print(f"{frame_count} frames were saved in the folder '{folders['imgs_folder_A']}'.")

    td.crear_video(folders["imgs_folder_A"], folders["video_dir"], fps=30, codec='mp4v')

def main():
    # Parse command line arguments
    args = parse_arguments()
    # Create necessary folders
    folders = td.folder_creation(args.root)
    if args.root is None:
        args.root = folders["video_path"]
    # Save configuration to a YAML file
    guardar_configuracion(args)
    # Process video and extract frames
    procesar_video(folders)

if __name__ == "__main__":
    main()