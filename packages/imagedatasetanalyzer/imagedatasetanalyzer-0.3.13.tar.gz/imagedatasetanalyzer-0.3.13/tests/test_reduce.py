import sys
import os
import torch
import numpy as np




sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from imagedatasetanalyzer.src.datasets.imagelabeldataset import ImageLabelDataset, ImageDataset
from imagedatasetanalyzer.src.models.kmeansclustering import KMeansClustering
from imagedatasetanalyzer.src.models.agglomerativeclustering import AgglomerativeClustering
from imagedatasetanalyzer.src.models.dbscanclustering import DBSCANClustering
from imagedatasetanalyzer.src.models.opticsclustering import OPTICSClustering


if __name__ == "__main__":
    
    img_dir = r"C:\Users\joortif\Desktop\datasets\Preprocesados\forest_freiburg_multiclass\train\images"
    labels_dir = r"C:\Users\joortif\Desktop\datasets\Preprocesados\forest_freiburg_multiclass\train\labels"
    output_path = r"C:\Users\joortif\Desktop\results\plots"
    analysis_path = r"C:\Users\joortif\Desktop\Resultados_ImageDatasetAnalyzer\freiburg_resultados\analysis"

    os.makedirs(os.path.join(output_path, "kmeans"), exist_ok=True)
    os.makedirs(os.path.join(output_path, "agglomerative"), exist_ok=True)
    os.makedirs(os.path.join(output_path, "dbscan"), exist_ok=True)
    os.makedirs(os.path.join(output_path, "optics"), exist_ok=True)

    kmeans_output_path = os.path.join(output_path, "kmeans")
    agglomerative_output_path = os.path.join(output_path, "agglomerative")
    dbscan_output_path = os.path.join(output_path, "dbscan")
    optics_output_path = os.path.join(output_path, "optics")

    os.makedirs(os.path.join(kmeans_output_path, "elbow"), exist_ok=True)
    os.makedirs(os.path.join(kmeans_output_path, "calinski"), exist_ok=True)

    kmeans_elbow_path = os.path.join(kmeans_output_path, "elbow")
    kmeans_silhouette_path = os.path.join(kmeans_output_path, "calinski")

    random_state = 123

    dataset = ImageDataset(img_dir)
    label_dataset = ImageLabelDataset(img_dir=img_dir, label_dir=labels_dir, background=0)

    #label_dataset.analyze(output=analysis_path, verbose=True)

    embeddings = np.load(r'C:\Users\joortif\Desktop\Resultados_ImageDatasetAnalyzer\embeddings\embeddings_labels.npy')
    
    kmeans = KMeansClustering(dataset, embeddings, random_state)
    agglomerative = AgglomerativeClustering(dataset, embeddings, random_state)
    dbscan = DBSCANClustering(dataset, embeddings, random_state)
    optics = OPTICSClustering(dataset, embeddings, None)

    res = dbscan.find_best_DBSCAN(np.arange(0.1,1.0), range(2,10), "silhouette", True, kmeans_silhouette_path, True)
    print(res)
    #reduced_dataset_kmeans = kmeans.select_balanced_images(2, 0.6, selection_type='diverse')
    #reduced_dataset_agg = agglomerative.select_balanced_images(2, 'single', 0.8, diverse_percentage=0, selection_type='random')
    #reduced_dataset_dbscan = dbscan.select_balanced_images(6.551724137931035, 18, 0.7, diverse_percentage=0.5)
    #reduced_dataset_optics = optics.select_balanced_images(12, 0.7, diverse_percentage=0.5)
