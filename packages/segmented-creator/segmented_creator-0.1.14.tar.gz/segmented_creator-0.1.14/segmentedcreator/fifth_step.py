import argparse
import os
import cv2
import segmentedcreator.tooldata as td
import sys
import yaml
import shutil
import csv
import numpy as np
import torch
from sam2.build_sam import build_sam2_video_predictor  # type: ignore
from IPython.display import clear_output

# Initialize variables
estado_global = {
    "puntos_interes": [],
    "input_label": np.array([]),
    "terminar": False,
    "omitir": False,
    "inference_state": None,
    "predictor": None,
    "mask": [],
    "ann_obj_id": 1,
    "prompts": {},
    "class_id": None,
    "id_obj": None,
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
        raise ValueError("The scaling factor (--fac) is mandatory. At least in the first execution.")
    if args.sam2_chkpt is None:
        raise ValueError("The path to the SAM2 model checkpoint (--sam2_chkpt) is mandatory. At least in the first execution.")

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
        print("Predictor SAM2 configured successfully.")
        return predictor
    except Exception as e:
        print(f"Error configuring SAM2 predictor: {e}")
        sys.exit("Failed to configure SAM2 predictor. Please check the configuration and checkpoint files.")

def process_step(folders, args):
    global estado_global

    csv_path = folders["root"] + f"/track_dic.csv"

    files = [f for f in os.listdir(folders["mask_folder"]) if f.endswith(('.png', '.jpg', '.jpeg')) and f.startswith('outmask_fr0')]
    estado_global["id_obj"] = int(max(files, key=lambda x: int(x.split('_')[2][2:])).split('_')[2][2:]) + 1

    df, image_files, files = td.load_and_prepare_data(csv_path, folders["imgs_folder_A"])
    td.cleanup_temp_files(folders["frame_aux"], folders["recorte_folder"])

    # Initial configuration
    archivo_csv = folders["root"] + '/mask_list.csv'  # Path to the CSV file
    campos = ['ruta', 'frame_number', 'clase', 'id']  # Column headers

    # Check if the file exists to write headers
    with open(archivo_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()

    for j in range(len(df)):
        print(f'Processing object {j + 1} of {len(df)}')

        estado_global["puntos_interes"] = []
        estado_global["input_label"] = np.array([])
        estado_global["terminar"] = False
        estado_global["omitir"] = False

        # Process each row of the DataFrame
        row = df.iloc[j]
        frame_number = row["frame_number"] - 1 
            
        recorte, imagen, bbox, archivo = td.process_frame(
                row, image_files, folders["imgs_folder_A"], folders["frame_aux"], folders["frames_folder"], folders["recorte_folder"]
            )

        estado_global["inference_state"] = estado_global["predictor"].init_state(folders["recorte_folder"])
        estado_global["predictor"].reset_state(estado_global["inference_state"])
        td.handle_user_interaction(recorte, estado_global)

        if estado_global["terminar"] == True:
            print("Finishing the process.")
            break

        if estado_global["omitir"] == True:
            estado_global["omitir"] = False
        else:  
            com_mask = td.create_composite_mask(estado_global["mask"], imagen.shape, bbox)    
            nam_aux = f"fr{frame_number}_id{estado_global['id_obj']}_cl{estado_global['class_id']}.png"  

            cv2.imwrite(os.path.join(folders["traked_folder"], nam_aux), com_mask * 255)

            with open(archivo_csv, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writerow({'ruta': nam_aux, 
                                'frame_number': frame_number, 
                                'clase': estado_global["class_id"],
                                'id': estado_global["id_obj"]})

            shutil.rmtree(folders["aux_folder"])
            os.makedirs(folders["aux_folder"], exist_ok=True)

            estado_global["id_obj"] += 1
            com_mask = []
        clear_output(wait=False)

        td.cleanup_temp_files(folders["frame_aux"], folders["recorte_folder"])
        estado_global["predictor"].reset_state(estado_global["inference_state"])

        shutil.rmtree(folders["aux_folder"])
        os.makedirs(folders["aux_folder"], exist_ok=True)

def main():
    # Parsing command line arguments
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
        process_step(folders, args)
    except Exception as e:
        sys.exit(f"Error processing video: {e}")

if __name__ == "__main__":
    main()