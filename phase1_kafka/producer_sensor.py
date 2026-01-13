from kafka import KafkaProducer
import json
import time
import random
import sys

# Récupère le NODE_ID depuis la ligne de commande
NODE_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1
TOPIC = f'sensor-data-node-{NODE_ID}'

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"🔧 Capteur Node {NODE_ID} démarré sur topic: {TOPIC}")

try:
    while True:
        data = {
            'timestamp': time.time(),
            'node_id': NODE_ID,
            'temperature': random.uniform(20.0, 80.0),
            'vibration': random.uniform(0.0, 10.0),
            'pressure': random.uniform(1.0, 5.0)
        }
        
        producer.send(TOPIC, value=data)
        print(f"📤 Node {NODE_ID} - Temp: {data['temperature']:.1f}°C, Vib: {data['vibration']:.1f}Hz")
        time.sleep(2)

except KeyboardInterrupt:
    print(f"\n🛑 Capteur Node {NODE_ID} arrêté")
    producer.close()