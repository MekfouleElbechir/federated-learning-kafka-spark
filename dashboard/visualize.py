from kafka import KafkaConsumer
import json
import time

consumer = KafkaConsumer(
    'model-weights',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("📊 DASHBOARD DÉMARRÉ")
print("=" * 80)

losses = {1: [], 2: []}

try:
    for message in consumer:
        data = message.value
        node_id = data['node_id']
        loss = data['loss']
        weights = data['weights']
        
        losses[node_id].append(loss)
        avg = sum(losses[node_id]) / len(losses[node_id])
        
        emoji = "🔵" if node_id == 1 else "🟢"
        print(f"{emoji} Node {node_id} | Loss: {loss:.4f} | Avg: {avg:.4f} | w1={weights['w1']:.3f}")

except KeyboardInterrupt:
    print("\n🛑 Dashboard arrêté")
finally:
    consumer.close()