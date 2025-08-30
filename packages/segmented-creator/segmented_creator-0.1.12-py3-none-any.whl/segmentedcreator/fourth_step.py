import argparse
from html import parser
import os
import cv2
import segmentedcreator.tooldata as td
import sys
import yaml
from tqdm import tqdm
from deep_sort_realtime.deepsort_tracker import DeepSort
from sahi import AutoDetectionModel

# Initialize variables
estado_global = {
    "track_dict": {},
    "sahi_model": None,
    "tracker": None,
}

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

    # Load previous config if exists
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        # Fill in any unspecified CLI arguments
        for key, value in config_data.items():
            if getattr(args, key) is None:
                setattr(args, key, value)

    return args

def check_args(args):
    if args.fac is None:
        raise ValueError("The scale factor (--fac) is mandatory. At least on the first run.")
    if args.sam2_chkpt is None:
        raise ValueError("The path to the SAM2 model checkpoint (--sam2_chkpt) is mandatory. At least on the first run.")

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

def model_config():
    ### SAHI model for enhanced detection
    estado_global["sahi_model"] = AutoDetectionModel.from_pretrained(
        model_type='ultralytics',
        model_path='yolo11x.pt',
        confidence_threshold=0.35,
        device="cuda" if cv2.cuda.getCudaEnabledDeviceCount() > 0 else "cpu"
    )

    ### Tracker DeepSort
    estado_global["tracker"] = DeepSort(max_age=30, n_init=3, nn_budget=100, override_track_class=None)

def process_step(folders, args):
    classes=[0, 1, 2, 3, 5, 7]  # Classes of interest: 0=person, 1=bicycle, 2=car, 3=motorcycle, 5=bus, 7=truck
    cap = cv2.VideoCapture(folders["video_dir"])
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    with tqdm(total=total_frames, desc="Processing Video", unit='frame') as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("No frame captured or end of video.")
                break

            frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

            # 0. Prepare the frame
            frame = td.apply_inverse_mask(frame, os.path.join(folders["frames_folder"], f"{frame_number}.png"))

            # 1. Detection with SAHI (better accuracy)
            sahi_predictions = td.detect_with_sahi(frame, estado_global["sahi_model"], args.img_size_sahi, args.overlap_sahi)

            # 2. Convert detections to DeepSort format
            detections = td.convert_sahi_to_deepsort(sahi_predictions)

            # 3. Filter by classes of interest
            filtered_detections = [d for d in detections if d[2] in classes]

            # 4. Tracking with DeepSort
            tracks = estado_global["tracker"].update_tracks(filtered_detections, frame=frame)

            # 5. Update tracking information
            estado_global["track_dict"] = td.update_tracking_info(tracks, frame_number, estado_global["track_dict"])

            pbar.update(1)

    td.save_tracking_info(estado_global["track_dict"], folders["root"] + f"/track_dic.csv")
    cap.release()

def main():
    # Parse command line arguments
    args = parse_arguments()
    # Check required arguments
    check_args(args)
    # Create necessary folders
    folders = td.folder_creation(args.root)
    # Save configuration to a YAML file
    guardar_configuracion(args)

    # Configure SAHI model and tracker
    model_config()

    try:
        process_step(folders, args)
    except Exception as e:
        sys.exit(f"Error processing video: {e}")

if __name__ == "__main__":
    main()