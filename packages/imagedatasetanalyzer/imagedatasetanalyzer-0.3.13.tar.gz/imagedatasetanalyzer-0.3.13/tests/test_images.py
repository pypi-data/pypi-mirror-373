import os
import random
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from math import ceil, sqrt
import numpy as np

def mostrar_mosaico_imagenes(directorio, N, titulo):
    imagenes = [f for f in os.listdir(directorio) if f.lower().endswith('.png')]

    N = min(N, len(imagenes))

    imagenes_seleccionadas = random.sample(imagenes, N)

    cols = ceil(sqrt(N))
    rows = ceil(N / cols)

    fig, axs = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3))

    # Aplanar los ejes si es necesario
    axs = axs.flatten() if isinstance(axs, (list, np.ndarray)) else [axs]

    for i in range(rows * cols):
        ax = axs[i]
        ax.axis('off')  # Quitar ejes

        if i < N:
            ruta = os.path.join(directorio, imagenes_seleccionadas[i])
            img = mpimg.imread(ruta)
            ax.imshow(img)
            ax.set_title(imagenes_seleccionadas[i], fontsize=8)

    if titulo:
        plt.suptitle(titulo, fontsize=16)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

mostrar_mosaico_imagenes(r"C:\Users\joortif\Desktop\resultados\results_busi\representative", 12, titulo="12 Sample Images Using Centroid Based Selection")
