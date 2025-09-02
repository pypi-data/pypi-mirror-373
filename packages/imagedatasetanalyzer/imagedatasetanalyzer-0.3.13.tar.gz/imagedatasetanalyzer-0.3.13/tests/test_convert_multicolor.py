import numpy as np
import gc
import os
import cv2
from tqdm import tqdm
from PIL import Image

def save_multilabel_mask(mask, file_name, output_dir: str, save_as: str="bgr"):
        mask_filename = os.path.splitext(file_name)[0] + ".png"
        mask_filepath = os.path.join(output_dir, mask_filename)
        if save_as == "bgr":
            cv2.imwrite(mask_filepath, cv2.cvtColor(mask, cv2.COLOR_RGB2BGR))
        elif save_as == "gray":
            cv2.imwrite(mask_filepath, cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY))


def transform(input_data: str, output_dir: str, color_mask: dict):
        masks = []

        label_files = [f for f in os.listdir(input_data) if os.path.isfile(os.path.join(input_data, f))]

        os.makedirs(output_dir, exist_ok=True)

        for filename in tqdm(label_files, desc="Converting grayscale masks to color masks..."):
            label_path = os.path.join(input_data, filename)
            gray_mask = cv2.imread(label_path, cv2.IMREAD_GRAYSCALE)

            color_mask_img = np.zeros((*gray_mask.shape, 3), dtype=np.uint8)

            for class_id, color in color_mask.items():
                mask_class = gray_mask == class_id
                color_mask_img[mask_class] = color

            save_multilabel_mask(color_mask_img, filename, output_dir)
            masks.append(color_mask_img)

            del gray_mask, color_mask_img
            gc.collect()

        return masks

def calculate_class_pixel_proportions(label_dir: str, num_classes: int, background: int | None = None) -> np.ndarray:
    """
    Calcula la proporción de píxeles de cada clase en todo el dataset de segmentación.

    Args:
        label_dir (str): Ruta a la carpeta que contiene las máscaras (.png) multiclase.
        num_classes (int): Número total de clases.
        background (int | None): ID de clase que debe ignorarse (opcional).

    Returns:
        np.ndarray: Array de tamaño (num_classes,) con proporciones de píxeles por clase (suman 1.0).
    """
    total_counts = np.zeros(num_classes, dtype=np.int64)
    total_pixels = 0

    mask_files = [f for f in os.listdir(label_dir) if f.endswith(".png")]

    for filename in tqdm(mask_files, desc="Computing class pixel proportions"):
        mask_path = os.path.join(label_dir, filename)
        mask = np.array(Image.open(mask_path))

        unique, counts = np.unique(mask, return_counts=True)

        for class_id, count in zip(unique, counts):
            if background is not None and class_id == background:
                continue
            if class_id < num_classes:
                total_counts[class_id] += count
                total_pixels += count

    proportions = total_counts / total_pixels
    return proportions

def reduce_labels_id(input_data: str, output_dir: str, label_dict: dict):
    masks = []

    label_files = [f for f in os.listdir(input_data) if os.path.isfile(os.path.join(input_data, f))]

    os.makedirs(output_dir, exist_ok=True)

    for filename in tqdm(label_files, desc="Reducing label ids..."):
        label_path = os.path.join(input_data, filename)
        gray_mask = cv2.imread(label_path, cv2.IMREAD_GRAYSCALE)

        converted_mask = np.zeros_like(gray_mask, dtype=np.uint8)

        for original_ids, new_id in label_dict.items():
            if isinstance(original_ids, int):
                mask_class = (gray_mask == original_ids)
            elif isinstance(original_ids, (tuple, list, set)):
                mask_class = np.isin(gray_mask, list(original_ids))
            else:
                raise ValueError(f"Unsupported key type: {type(original_ids)} in label_dict")

            converted_mask[mask_class] = new_id

        save_multilabel_mask(converted_mask, filename, output_dir)
        masks.append(converted_mask)

        del gray_mask, converted_mask
        gc.collect()

    return masks

def count_unique_ids(input_dir: str):
    unique_ids = set()
    
    label_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]

    for filename in tqdm(label_files, desc="Contando IDs únicos..."):
        label_path = os.path.join(input_dir, filename)
        gray_mask = cv2.imread(label_path, cv2.IMREAD_GRAYSCALE)
        
        if gray_mask is None:
            print(f"Advertencia: no se pudo leer la imagen {filename}")
            continue

        unique_in_mask = np.unique(gray_mask)
        unique_ids.update(unique_in_mask.tolist())

    return sorted(unique_ids)


# img_dir = r"C:\Users\joortif\Desktop\datasets\Completos\CamVid\images"
img_dir = r"C:\Users\joortif\Desktop\datasets\Completos\melanoma_3c\full_converted\images"
labels_dir = r"C:\Users\joortif\Desktop\datasets\Completos\melanoma_3c\full_converted\labels"
output_dir = r"C:\Users\joortif\Desktop\datasets\Completos\melanoma_3c\full_converted\multicolor"
#output_dir2 = r"C:\Users\joortif\Desktop\datasets\Completos\CamVid\labels_reduced_color"
color_mask = {
    0: (255, 0, 0),
    1: (0, 255, 0),
    2: (0, 0, 255),
    3: (255,255,255)

}


# color_mask = {
#        0: (166,206,227),
#       1: (31,120,180),
#        2: (178,223,138),
#        3: (51,160,44),
#        4: (251,154,153),
#        5: (227,26,28),
#        6: (253,191,111)
# }

transform(labels_dir, output_dir, color_mask)
#transform(output_dir, output_dir2, color_mask)

old2new = {
        0: 0,
        (1,2,6,7,11): 1,
        3: 2,
        4: 3,
        5: 4,
        8: 5,
        (9,10): 6 
}

def es_gris(imagen):
    if len(imagen.shape) == 2:
        # Tiene solo una dimensión de color: es escala de grises
        return True
    elif len(imagen.shape) == 3:
        # Tiene 3 canales (RGB o BGR)
        b, g, r = cv2.split(imagen)
        return np.array_equal(b, g) and np.array_equal(b, r)
    else:
        return False

# Directorio con tus imágenes
"""directorio = output_dir

for archivo in os.listdir(directorio):
    if archivo.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        ruta = os.path.join(directorio, archivo)
        img = cv2.imread(ruta)
        if es_gris(img):
            print(f"{archivo} → Escala de grises")
        else:
            print(f"{archivo} → RGB o color")

#reduce_labels_id(labels_dir, output_dir, old2new)
new_ids = count_unique_ids(output_dir)
print(new_ids)"""