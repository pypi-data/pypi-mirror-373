import os

from imagedatasetanalyzer.src.datasets.imagedataset import ImageDataset
from imagedatasetanalyzer.src.embeddings.huggingfaceembedding import HuggingFaceEmbedding
from imagedatasetanalyzer.src.models.kmeansclustering import KMeansClustering


if __name__ == "__main__":

    img_dir = r"C:\Users\joortif\Desktop\datasets\Completos\CamVid\images"
    output_dir = r"C:\Users\joortif\Desktop\resultados\results_camvid"

    image_dataset = ImageDataset(img_dir)

    embedding_generator = HuggingFaceEmbedding(model_name="google/vit-base-patch16-224")
    embeddings = embedding_generator.generate_embeddings(image_dataset)

    kmeans = KMeansClustering(image_dataset, embeddings, random_state=123)

    # results es una tupla con forma (mejor_num_clusters, mejor_score_calinski, etiquetas_obtenidas)
    results = kmeans.find_best_n_clusters(range(2,25), 'calinski', plot=False)

    for strategy in ['representative','diverse','random']:
        reduced_dataset = kmeans.select_balanced_images(results[0], retention_percentage=0.7, selection_type=strategy,
                                                        diverse_percentage=0.0, output_directory=os.path.join(output_dir, strategy))