import sys
import os
import torch
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from imagedatasetanalyzer.datasets.imagedataset import ImageDataset
from imagedatasetanalyzer.datasets.imagelabeldataset import ImageLabelDataset

if __name__ == "__main__":

    import logging
    logging.basicConfig(level=logging.INFO)

    img_dir = r"C:\Users\joortif\Desktop\datasets\Completos\melanoma\full\images"
    labels_dir = r"C:\Users\joortif\Desktop\datasets\Completos\melanoma\full\converted_labels"
    output_dir = r"C:\Users\joortif\Desktop\datasets\results\results_camvid_reduced"

    #img_dir = r"C:\Users\joortif\Desktop\datasets\Completos\CamVid\images"
    #labels_dir = r"C:\Users\joortif\Desktop\datasets\Completos\CamVid\labels"
    image_dataset = ImageDataset(img_dir)

    mode_h, mode_w = image_dataset.image_sizes()
    resize_h, resize_w = image_dataset.calculate_closest_resize(mode_h, mode_w)
    print(resize_h, resize_w)

    """imagelabel_dataset = ImageLabelDataset(img_dir=img_dir, label_dir=labels_dir, class_map={0: "sky",
    1: "obstacle",
    2: "road",
    3: "sidewalk",
    4: "vegetation",
    5: "vehicle",
    6: "person"})
    imagelabel_dataset.analyze(verbose=True, similarity_index=None, output=output_dir)"""

    #image_dataset = ImageDataset(img_dir=img_dir)
    #image_dataset.analyze(similarity_index=None, verbose=False)