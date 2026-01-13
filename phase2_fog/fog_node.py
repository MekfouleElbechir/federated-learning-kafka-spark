from kafka import KafkaConsumer, KafkaProducer
import json
import time
import sys
import random

NODE_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1
TOPIC_INPUT = f'sensor-data-node-{NODE_ID}'
TOPIC_WEIGHTS = 'model-weights'

consumer = KafkaConsumer(
    TOPIC_INPUT,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"🌫️ FOG NODE {NODE_ID} DÉMARRÉ")
print(f"📡 Lecture: {TOPIC_INPUT} | 📤 Envoi: {TOPIC_WEIGHTS}")

# Modèle simple
model_weights = {'w1': random.uniform(-1, 1), 'w2': random.uniform(-1, 1), 'w3': random.uniform(-1, 1)}
batch_count = 0
BATCH_SIZE = 5
total_loss = 0

try:
    for message in consumer:
        data = message.value
        temp = data.get('temperature', 0)
        vibration = data.get('vibration', 0)
        pressure = data.get('pressure', 0)
        
        # Détection anomalie
        is_anomaly = temp > 70 or vibration > 8
        
        # Calcul loss
        prediction = model_weights['w1']*temp/100 + model_weights['w2']*vibration/10 + model_weights['w3']*pressure/5
        target = 1.0 if is_anomaly else 0.0
        loss = abs(target - prediction)
        total_loss += loss
        
        status = "🚨 ANOMALIE" if is_anomaly else "✅ NORMAL"
        print(f"{status} | Node {NODE_ID} | Temp: {temp:.1f}°C | Vib: {vibration:.1f}Hz | Loss: {loss:.3f}")
        
        # Apprentissage
        model_weights['w1'] -= 0.01 * (loss - 0.5)
        model_weights['w2'] -= 0.01 * (loss - 0.5)
        model_weights['w3'] -= 0.01 * (loss - 0.5)
        
        batch_count += 1
        
        # Envoi poids
        if batch_count >= BATCH_SIZE:
            avg_loss = total_loss / BATCH_SIZE
            weights_data = {
                'node_id': NODE_ID,
                'timestamp': time.time(),
                'weights': model_weights.copy(),
                'loss': avg_loss
            }
            producer.send(TOPIC_WEIGHTS, value=weights_data)
            print(f"📤 Node {NODE_ID} - POIDS ENVOYÉS | Loss: {avg_loss:.3f}")
            print("-" * 60)
            batch_count = 0
            total_loss = 0

except KeyboardInterrupt:
    print(f"\n🛑 Fog Node {NODE_ID} arrêté")
finally:
    consumer.close()
    producer.close()