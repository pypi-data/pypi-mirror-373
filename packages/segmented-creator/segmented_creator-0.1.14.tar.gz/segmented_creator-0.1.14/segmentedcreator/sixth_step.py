import argparse
import os
import segmentedcreator.tooldata as td
import sys
import yaml
import shutil
import numpy as np
import torch
import pandas as pd
from sam2.build_sam import build_sam2_video_predictor  # type: ignore
from IPython.display import clear_output

# Initialize variables
estado_global = {
    "inference_state": None,
    "predictor": None,
    "video_segments": {},
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

    # Load previous config if it exists
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
    # Load current configuration if it exists
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
        # Activar bfloat16 globalmente
        torch.autocast("cuda", dtype=torch.bfloat16).__enter__()

        # Activar tf32 en GPUs Ampere (Compute Capability >= 8)
        if torch.cuda.get_device_properties(0).major >= 8:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True

    try:
        predictor = build_sam2_video_predictor(model_cfg, sam2_checkpoint, device=device)
        print("Predictor SAM2 configurado correctamente.")
        return predictor
    except Exception as e:
        print(f"Error al configurar el predictor SAM2: {e}")
        sys.exit("Fallo al configurar el predictor SAM2. Verifique la configuración y los archivos de checkpoint.")

def process_step(folders, args):
    archivo_csv = folders["root"] + '/mask_list.csv'  # Ruta del archivo CSV
    csv_path = folders["root"] + f"/track_dic.csv"
    df_a = pd.read_csv(archivo_csv)

    _, image_files, files = td.load_and_prepare_data(csv_path, folders["imgs_folder_A"])
    t_imgs = len(files)

    for k in range(len(df_a)):
        print(f'Procesando objeto {k + 1} de {len(df_a)}')

        # Procesar cada fila del DataFrame
        row = df_a.iloc[k]
        ruta_acc = row["ruta"]
        frame_number = row["frame_number"]
        class_id = row["clase"]
        id_obj = row["id"]

        com_mask = td.read_mask(os.path.join(folders["traked_folder"], ruta_acc))
        com_mask_aux = com_mask.copy()

        # Crear mascaras de la fila
        i = frame_number
        while i < t_imgs:
            lote = image_files[i:i + args.n_imgs]

            ### Copiamos n cantidad de imagenes a carpeta auxiliar
            for archivo in lote:
                shutil.copy(os.path.join(folders["imgs_folder_A"], archivo), os.path.join(folders["aux_folder"], archivo))

            print(f'copiando imagenes de {i} hasta {i + args.n_imgs - 1}')

            ### Iniciamos inferencia
            estado_global["inference_state"] = estado_global["predictor"].init_state(video_path=folders["aux_folder"])

            estado_global["video_segments"] = {}

            ### Iniciar procesamiento de mascaras
            td.add_object_mask(com_mask, id_obj, estado_global["predictor"], estado_global["inference_state"], 0)
            td.actualizar_segmentos_video(estado_global["predictor"], estado_global["inference_state"], estado_global["video_segments"])
            td.save_masks(folders["mask_folder"], args.n_imgs, i, estado_global["video_segments"], class_id, True)

            ### Eliminar imagenes de carpeta auxiliar
            files_aux = sorted(os.listdir(folders["aux_folder"]))

            for archivo in files_aux[:-1]:
                os.remove(os.path.join(folders["aux_folder"], archivo))

            # cargar nueva mascara
            i += args.n_imgs
            estado_global["predictor"].reset_state(estado_global["inference_state"])
            _, com_mask = next(iter(estado_global["video_segments"][len(estado_global["video_segments"])-1].items()))
            com_mask = com_mask[0].astype(np.uint8)

        shutil.rmtree(folders["aux_folder"])
        os.makedirs(folders["aux_folder"], exist_ok=True)

        com_mask = com_mask_aux

        ##### Procesar imagenes en reversa #####
        i = frame_number
        while i > 0:
            lote = image_files[max(0, i - args.n_imgs):i+1]

            for archivo in lote:
                shutil.copy(os.path.join(folders["imgs_folder_A"], archivo), os.path.join(folders["aux_folder"], archivo))

            print(f'copiando imagenes de {max(0, i - args.n_imgs)} hasta {i}')

            estado_global["inference_state"] = estado_global["predictor"].init_state(video_path=folders["aux_folder"])
            estado_global["video_segments"] = {}

            td.add_object_mask(com_mask, id_obj, estado_global["predictor"], estado_global["inference_state"], len(lote)-1)
            td.actualizar_segmentos_video(estado_global["predictor"], estado_global["inference_state"], estado_global["video_segments"], reverse=True)
            td.save_masks(folders["mask_folder"], args.n_imgs, max(0, i - args.n_imgs), estado_global["video_segments"], class_id, True)

            ### Eliminar imagenes de carpeta auxiliar
            files_aux = sorted(os.listdir(folders["aux_folder"]))

            for archivo in files_aux[1:]:
                os.remove(os.path.join(folders["aux_folder"], archivo))

            i -= args.n_imgs
            estado_global["predictor"].reset_state(estado_global["inference_state"])
            _, com_mask = next(iter(estado_global["video_segments"][len(estado_global["video_segments"])-1].items()))
            com_mask = com_mask[0].astype(np.uint8)

        id_obj += 1
        com_mask = []
        clear_output(wait=False)

    td.cleanup_temp_files(folders["frame_aux"], folders["recorte_folder"])
    estado_global["predictor"].reset_state(estado_global["inference_state"])

    shutil.rmtree(folders["aux_folder"])
    os.makedirs(folders["aux_folder"], exist_ok=True)
    print('Proceso completado. Todas las mascaras han sido procesadas y guardadas.')

def main():
    # Parse command line arguments
    args = parse_arguments()
    # Check necessary arguments
    check_args(args)
    # Create necessary folders
    folders = td.folder_creation(args.root)
    # Save the configuration to a YAML file
    guardar_configuracion(args)

    # Configure the SAM2 predictor
    estado_global["predictor"] = configurar_sam2_predictor(args.model_cfg, args.sam2_chkpt)

    try:
        process_step(folders, args)
        td.group_masks_color(folders["mask_folder"], folders["semantic_folder"])
    except Exception as e:
        sys.exit(f"Error processing video: {e}")

if __name__ == "__main__":
    main()