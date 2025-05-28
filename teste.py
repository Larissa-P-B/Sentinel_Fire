import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, jsonify

# Simulação de sensor térmico
def simulate_thermal_image(size=(10, 10), fire_spot=None):
    image = np.random.normal(30, 5, size)  # Temperatura base (~30°C)
    if fire_spot:
        x, y = fire_spot
        image[x-1:x+2, y-1:y+2] = np.random.normal(80, 10, (3, 3))  # Foco de fogo
    return image

# API simulada
app = Flask(__name__)
@app.route('/thermal')
def thermal():
    image = simulate_thermal_image(fire_spot=(5, 5))  # Fogo no pixel (5,5)
    return jsonify({"image": image.tolist()})

# Detecção de fogo
thermal_data = simulate_thermal_image(fire_spot=(3, 3))
fire_mask = thermal_data > 60  # Limiar de detecção

# Visualização
plt.imshow(thermal_data, cmap='hot')
plt.title("Simulação de Imagem Térmica")
plt.colorbar()
plt.show()