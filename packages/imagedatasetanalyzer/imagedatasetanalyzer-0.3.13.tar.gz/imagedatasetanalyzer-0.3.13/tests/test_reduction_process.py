import torch
import cv2
import numpy as np
import time
import csv
import random
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from torch.utils.data import DataLoader
from torch.utils.data import Dataset as BaseDataset
import albumentations as A
import warnings
import pytorch_lightning as pl
import segmentation_models_pytorch as smp

import torch
from torch.optim import lr_scheduler
import pandas as pd


from torchvision import models, transforms


import os
import numpy as np
from PIL import Image
from collections import defaultdict

def contar_imagenes_por_clase(directorio):
    clases_por_imagen = defaultdict(int)

    for archivo in os.listdir(directorio):
        if archivo.lower().endswith(".png"):
            ruta_imagen = os.path.join(directorio, archivo)
            try:
                imagen = Image.open(ruta_imagen).convert("L")
                np_imagen = np.array(imagen)
                
                # Obtener clases únicas en la imagen
                clases_en_imagen = np.unique(np_imagen)

                # Contar cada clase como presente en esta imagen
                for clase in clases_en_imagen:
                    clases_por_imagen[clase] += 1

            except Exception as e:
                print(f"Error procesando {archivo}: {e}")

    return dict(sorted(clases_por_imagen.items()))

conteo_clases = contar_imagenes_por_clase(r"C:\Users\joortif\Desktop\datasets\Completos\melanoma_3c\full_converted\labels")

for clase, cantidad in conteo_clases.items():
    print(f"Clase {clase}: presente en {cantidad} imagen(es)")



"""colores_normalizados = [
    (0.22, 0.49, 0.72),  # azul medio
    (0.30, 0.69, 0.29),  # verde medio
    (0.87, 0.35, 0.34),  # rojo apagado
    (1.00, 0.65, 0.00)   # naranja fuerte
]

def generar_datos_y_graficar(num_grupos=3, puntos_por_grupo=50, 
                             seleccionadas=3, criterio='cercanas', semilla=42,
                             colores_grupos=colores_normalizados, rango_centro=20, desviacion=1.0):
    np.random.seed(semilla)
    
    datos = []
    etiquetas = []
    
    centros = np.random.uniform(0, rango_centro, size=(num_grupos, 2))
    
    for i, centro in enumerate(centros):
        # Puntos con desviacion estándar controlada
        grupo = np.random.randn(puntos_por_grupo, 2) * desviacion + centro
        datos.append(grupo)
        etiquetas += [i] * puntos_por_grupo
    
    datos = np.vstack(datos)
    etiquetas = np.array(etiquetas)
    
    centroides = np.array([datos[etiquetas == i].mean(axis=0) for i in range(num_grupos)])
    
    plt.figure(figsize=(8, 6))
    
    if colores_grupos is None:
        cmap = plt.cm.get_cmap('tab10', num_grupos)
        colores = [cmap(i) for i in range(num_grupos)]
    else:
        if len(colores_grupos) < num_grupos:
            raise ValueError("La lista de colores debe tener al menos tantos colores como grupos.")
        colores = colores_grupos
    
    for i in range(num_grupos):
        grupo_datos = datos[etiquetas == i]
        
        plt.scatter(grupo_datos[:, 0], grupo_datos[:, 1], 
                    color=colores[i], label=f'Grupo {i+1}')
        
        if criterio is not None:
            distancias = np.linalg.norm(grupo_datos - centroides[i], axis=1)
            
            if criterio == 'cercanas':
                indices_selec = np.argsort(distancias)[:seleccionadas]
            elif criterio == 'lejanas':
                indices_selec = np.argsort(distancias)[-seleccionadas:]
            elif criterio == 'aleatorias':
                indices_selec = np.random.choice(len(grupo_datos), seleccionadas, replace=False)
            else:
                raise ValueError("Criterio debe ser 'cercanas', 'lejanas', 'aleatorias' o None")
            
            # Marcar puntos seleccionados
            plt.scatter(grupo_datos[indices_selec, 0], grupo_datos[indices_selec, 1], 
                        color='red', edgecolor='black', s=100, label=f'Seleccionados G{i+1}')

        
    plt.grid(False)  # Aquí sin cuadriculas
    plt.tight_layout()
    plt.show()


# Ejemplo: grupos cerca y poco dispersos
generar_datos_y_graficar(num_grupos=4, puntos_por_grupo=50, seleccionadas=15,
                         criterio=None, rango_centro=8, desviacion=0.5)"""

