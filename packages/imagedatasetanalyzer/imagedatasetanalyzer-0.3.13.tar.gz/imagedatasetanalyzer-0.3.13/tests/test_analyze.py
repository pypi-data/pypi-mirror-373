import sys
import os
import torch
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from imagedatasetanalyzer.datasets.imagedataset import ImageDataset
from imagedatasetanalyzer.datasets.imagelabeldataset import ImageLabelDataset
from imagedatasetanalyzer.embeddings.tensorflowembedding import TensorflowEmbedding
from imagedatasetanalyzer.embeddings.torchembedding import PyTorchEmbedding
from imagedatasetanalyzer.embeddings.huggingfaceembedding import HuggingFaceEmbedding
from imagedatasetanalyzer.embeddings.opencvlbpembedding import OpenCVLBPEmbedding

if __name__ == "__main__":

    img_dir = r"C:\Users\joortif\Desktop\datasets\Completos\BUSI\full\images"
    labels_dir = r"C:\Users\joortif\Desktop\datasets\Completos\BUSI\full\labels"
    output_dir = r"C:\Users\joortif\Desktop\resultados\results_busi"

    imagelabel_dataset = ImageLabelDataset(img_dir=img_dir, label_dir=labels_dir)

    emb = OpenCVLBPEmbedding(radius=16, num_points=4, resize_height=384, resize_width=384)
    embeddings = emb.generate_embeddings(imagelabel_dataset)
    
    for file, emb in embeddings.items():
        print(f"{file} : {emb}")
    print(type(embeddings))
