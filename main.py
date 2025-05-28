import numpy as np
import cv2
import matplotlib.pyplot as plt
from flask import Flask, jsonify
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, GlobalAveragePooling2D
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import random
from threading import Thread
import time


# ==============================================
# Módulo 1: Sistema de Monitoramento (Simulado)
# ==============================================

class SensorSimulator:
    def __init__(self):
        self.temperature_range = (20, 50)  # °C normal
        self.fire_temperature = (80, 120)  # °C fogo
        self.humidity_range = (30, 70)  # % umidade
        self.co2_range = (300, 1000)  # ppm CO2 normal
        self.fire_co2 = (1000, 5000)  # ppm CO2 fogo

    def generate_thermal_image(self, size=(224, 224), has_fire=False):
        """Gera uma imagem térmica simulada"""
        img = np.random.randint(self.temperature_range[0], self.temperature_range[1], (*size, 3)).astype(np.uint8)
        if has_fire:
            x, y = np.random.randint(50, 174, 2)
            fire_size = random.randint(10, 30)
            img[x - fire_size:x + fire_size, y - fire_size:y + fire_size] = np.random.randint(
                self.fire_temperature[0], self.fire_temperature[1],
                (fire_size * 2, fire_size * 2, 3))
        return cv2.applyColorMap(img, cv2.COLORMAP_HOT)

    def generate_sensor_data(self, has_fire=False):
        """Gera dados simulados de temperatura, umidade e CO2"""
        if has_fire:
            temp = random.uniform(self.fire_temperature[0], self.fire_temperature[1])
            co2 = random.uniform(self.fire_co2[0], self.fire_co2[1])
            humidity = random.uniform(self.humidity_range[0], self.humidity_range[1] * 0.7)  # Umidade diminui no fogo
        else:
            temp = random.uniform(self.temperature_range[0], self.temperature_range[1])
            co2 = random.uniform(self.co2_range[0], self.co2_range[1])
            humidity = random.uniform(self.humidity_range[0], self.humidity_range[1])

        return {
            'temperature': temp,
            'humidity': humidity,
            'co2': co2,
            'has_fire': has_fire
        }


# ==============================================
# Módulo 2: Detecção por IA
# ==============================================

class FireDetectionModel:
    def __init__(self):
        self.model = self.build_model()
        self.sensor_simulator = SensorSimulator()

    def build_model(self):
        """Constroi um modelo CNN simples para classificação"""
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            MaxPooling2D(2, 2),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D(2, 2),
            Conv2D(128, (3, 3), activation='relu'),
            GlobalAveragePooling2D(),
            Dense(1, activation='sigmoid')
        ])

        model.compile(optimizer='adam',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        return model

    def generate_dataset(self, num_samples=1000):
        """Gera um dataset sintético para treinamento"""
        X = []
        y = []

        for i in range(num_samples):
            has_fire = random.random() > 0.5
            img = self.sensor_simulator.generate_thermal_image(has_fire=has_fire)
            X.append(img)
            y.append(1 if has_fire else 0)

        return np.array(X), np.array(y)

    def train_model(self, X_train, y_train, X_val, y_val, epochs=10):
        """Treina o modelo de detecção de fogo"""
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=32
        )

        # Plot training history
        plt.figure(figsize=(12, 4))
        plt.subplot(1, 2, 1)
        plt.plot(history.history['accuracy'], label='Train Accuracy')
        plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
        plt.legend()
        plt.title('Accuracy')

        plt.subplot(1, 2, 2)
        plt.plot(history.history['loss'], label='Train Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.legend()
        plt.title('Loss')
        plt.show()

    def evaluate_model(self, X_test, y_test):
        """Avalia o modelo nos dados de teste"""
        y_pred = (self.model.predict(X_test) > 0.5).astype(int)
        print(classification_report(y_test, y_pred))
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

    def simulate_real_time_detection(self, duration=30):
        """Simula a detecção em tempo real"""
        start_time = time.time()
        alert_count = 0

        while time.time() - start_time < duration:
            # Simula uma nova leitura (10% de chance de fogo)
            has_fire = random.random() < 0.1
            img = self.sensor_simulator.generate_thermal_image(has_fire=has_fire)
            sensor_data = self.sensor_simulator.generate_sensor_data(has_fire)

            # Previsão do modelo
            img_input = np.expand_dims(img, axis=0) / 255.0
            fire_prob = self.model.predict(img_input)[0][0]

            # Sistema de alerta
            status = "NORMAL"
            color = (0, 255, 0)  # Verde

            if fire_prob > 0.8:
                status = "ALERTA VERMELHO - FOGO DETECTADO!"
                color = (0, 0, 255)  # Vermelho
                alert_count += 1
            elif fire_prob > 0.5:
                status = "ALERTA AMARELO - POSSÍVEL FOGO"
                color = (0, 255, 255)  # Amarelo

            # Exibe os resultados
            display_img = img.copy()
            cv2.putText(display_img, status, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            sensor_text = f"Temp: {sensor_data['temperature']:.1f}°C | " \
                          f"Umidade: {sensor_data['humidity']:.1f}% | " \
                          f"CO2: {sensor_data['co2']:.1f}ppm"

            cv2.putText(display_img, sensor_text, (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow('Sistema de Detecção de Queimadas', display_img)
            if cv2.waitKey(500) == 27:  # Atualiza a cada 500ms ou ESC para sair
                break

        cv2.destroyAllWindows()
        print(f"\nSimulação concluída. Alertas de incêndio emitidos: {alert_count}")


# ==============================================
# Módulo 3: API de Controle (Simulada)
# ==============================================

app = Flask(__name__)
fire_detector = FireDetectionModel()


@app.route('/api/drone/status')
def drone_status():
    """Endpoint simulando status do drone"""
    return jsonify({
        'battery': random.randint(20, 100),
        'altitude': random.uniform(50, 150),
        'position': {
            'lat': -23.5 + random.uniform(-0.1, 0.1),
            'lng': -46.6 + random.uniform(-0.1, 0.1)
        },
        'is_online': True
    })


@app.route('/api/sensors/thermal')
def thermal_sensor():
    """Endpoint simulando sensor térmico"""
    has_fire = random.random() < 0.2  # 20% de chance de fogo para demonstração
    img = fire_detector.sensor_simulator.generate_thermal_image(has_fire=has_fire)
    _, img_encoded = cv2.imencode('.jpg', img)
    return jsonify({
        'image': img_encoded.tolist(),
        'has_fire': has_fire
    })


@app.route('/api/alerts', methods=['GET'])
def get_fire_alerts():
    """Endpoint que gera alertas de incêndio baseados na análise do modelo de IA"""
    # Simula a coleta de dados do sensor térmico
    has_fire = random.random() < 0.2  # 20% de chance de fogo para demonstração
    img = fire_detector.sensor_simulator.generate_thermal_image(has_fire=has_fire)

    # Pré-processamento da imagem para o modelo
    img_input = cv2.resize(img, (224, 224))
    img_input = np.expand_dims(img_input, axis=0) / 255.0

    # Predição do modelo
    fire_prob = float(fire_detector.model.predict(img_input)[0][0])

    # Gera dados ambientais simulados
    sensor_data = fire_detector.sensor_simulator.generate_sensor_data(has_fire)

    # Determina o nível de alerta
    alert_level = "normal"
    if fire_prob > 0.8:
        alert_level = "emergency"
    elif fire_prob > 0.5:
        alert_level = "warning"

    # Gera coordenadas simuladas (para exemplo)
    latitude = -23.5 + random.uniform(-0.1, 0.1)
    longitude = -46.6 + random.uniform(-0.1, 0.1)

    # Timestamp atual
    from datetime import datetime
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Converte a imagem para base64 para inclusão no JSON
    _, img_encoded = cv2.imencode('.jpg', img)
    import base64
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')

    return jsonify({
        "alert_id": f"alert_{random.randint(1000, 9999)}",
        "timestamp": timestamp,
        "alert_level": alert_level,
        "fire_probability": fire_prob,
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "sensor_data": {
            "temperature": sensor_data['temperature'],
            "humidity": sensor_data['humidity'],
            "co2": sensor_data['co2']
        },
        "thermal_image": img_base64,
        "actions_recommended": [
            "increase_surveillance" if alert_level == "warning" else None,
            "notify_fire_brigade" if alert_level == "emergency" else None
        ],
        "status": "new",
        "confidence": round(fire_prob * 100, 2)
    })
def run_flask_app():
    """Inicia o servidor Flask em uma thread separada"""
    app.run(port=5000, use_reloader=False)


# ==============================================
# Execução Principal
# ==============================================

if __name__ == "__main__":
    # Inicia a API em uma thread separada
    api_thread = Thread(target=run_flask_app)
    api_thread.daemon = True
    api_thread.start()

    # Cria e treina o modelo de detecção
    detector = FireDetectionModel()

    print("Gerando dataset sintético...")
    X, y = detector.generate_dataset(num_samples=500)
    X = X / 255.0  # Normaliza as imagens

    # Divide em treino/validação/teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25)

    print("\nTreinando modelo de detecção de queimadas...")
    detector.train_model(X_train, y_train, X_val, y_val, epochs=10)

    print("\nAvaliando modelo nos dados de teste:")
    detector.evaluate_model(X_test, y_test)

    # Simulação em tempo real
    print("\nIniciando simulação de detecção em tempo real (30 segundos)...")
    print("Pressione ESC para encerrar mais cedo.")
    detector.simulate_real_time_detection(duration=30)

    print(
        "\nSistema pronto para operação! Acesse http://localhost:5000/api/drone/status para ver os endpoints simulados.")