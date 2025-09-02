import argparse
import os
import cv2
import segmentedcreator.tooldata as td
import csv
import shutil
import numpy as np
import torch
import sys
import yaml

from sam2.build_sam import build_sam2_video_predictor # type: ignore

# Initialize variables
estado_global = {
    "prompts": {},
    "puntos_interes": [],
    "input_label": np.array([]),
    "ann_obj_id": 1,
    "mask": [],
    "predictor": None,
    "inference_state": None,
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
        raise ValueError("The scaling factor (--fac) is mandatory. At least on the first run.")
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

def configurar_sam2_predictor(model_cfg, sam2_checkpoint):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if device.type == "cuda":
        # Enable bfloat16 globally
        torch.autocast("cuda", dtype=torch.bfloat16).__enter__()

        # Enable tf32 on Ampere GPUs (Compute Capability >= 8)
        if torch.cuda.get_device_properties(0).major >= 8:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True

    try:
        predictor = build_sam2_video_predictor(model_cfg, sam2_checkpoint, device=device)
        print("SAM2 predictor configured correctly.")
        return predictor
    except Exception as e:
        print(f"Error configuring SAM2 predictor: {e}")
        sys.exit("Failed to configure SAM2 predictor. Check the configuration and checkpoint files.")

def process_step(folders, fac):
    shutil.rmtree(folders['aux_folder'])
    os.makedirs(folders['aux_folder'], exist_ok=True)

    # Load first frame
    files = os.listdir(folders['imgs_folder_A'])
    image_files = [f for f in sorted(files) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'))]

    # Initialize and show frame
    img = cv2.imread(os.path.join(folders['imgs_folder_A'], image_files[0]))
    h, w = img.shape[:2]
    scaled_frame = cv2.resize(img, (int(w / fac), int(h / fac)))
    cv2.imwrite(os.path.join(folders['frame_aux'], image_files[0]), scaled_frame)
    estado_global["inference_state"] = estado_global["predictor"].init_state(video_path=folders['frame_aux'])
    cv2.imshow("Frame", scaled_frame)
    cv2.setMouseCallback("Frame", td.on_click, param={"frame": scaled_frame, "estado": estado_global})

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 97:  # 'a' key
            class_id = td.get_class_from_user()
            estado_global["prompts"][estado_global["ann_obj_id"]] = (estado_global["puntos_interes"], estado_global["input_label"], class_id)
            estado_global["puntos_interes"] = []
            estado_global["input_label"] = np.array([])
            estado_global["ann_obj_id"] += 1

        elif key == 27:  # ESC key
            class_id = td.get_class_from_user()
            estado_global["prompts"][estado_global["ann_obj_id"]] = (estado_global["puntos_interes"], estado_global["input_label"], class_id)
            break

    cv2.destroyAllWindows()

    # Save dictionary to a CSV file
    with open(os.path.join(folders['root'], 'mask_prompts.csv'), 'w', newline='') as archivo:
        writer = csv.writer(archivo)
        for clave, valor in estado_global["prompts"].items():
            writer.writerow([clave, valor])

def main():
    # Parse command line arguments
    args = parse_arguments()
    # Check required arguments
    check_args(args)
    # Create necessary folders
    folders = td.folder_creation(args.root)
    # Save configuration to a YAML file
    guardar_configuracion(args)

    # Configure SAM2 predictor
    estado_global["predictor"] = configurar_sam2_predictor(args.model_cfg, args.sam2_chkpt)

    try:
       process_step(folders, args.fac)
    except Exception as e:
       sys.exit(f"Error processing video: {e}")

if __name__ == "__main__":
    main()