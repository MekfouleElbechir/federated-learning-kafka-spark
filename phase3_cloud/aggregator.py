from kafka import KafkaConsumer, KafkaProducer
import json
import numpy as np

consumer = KafkaConsumer(
    'model-weights',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("☁️ AGRÉGATEUR CLOUD DÉMARRÉ")

weights_buffer = {}
NUM_NODES = 2

try:
    for message in consumer:
        data = message.value
        node_id = data['node_id']
        
        print(f"📥 Reçu de Node {node_id} | Loss: {data['loss']:.3f}")
        weights_buffer[node_id] = data
        
        # Si on a tous les nodes
        if len(weights_buffer) >= NUM_NODES:
            print("🔄 AGRÉGATION...")
            
            # FedAvg: moyenne simple
            all_w1 = [weights_buffer[i]['weights']['w1'] for i in weights_buffer]
            all_w2 = [weights_buffer[i]['weights']['w2'] for i in weights_buffer]
            all_w3 = [weights_buffer[i]['weights']['w3'] for i in weights_buffer]
            
            global_weights = {
                'w1': np.mean(all_w1),
                'w2': np.mean(all_w2),
                'w3': np.mean(all_w3)
            }
            
            global_model = {
                'weights': global_weights,
                'timestamp': data['timestamp']
            }
            
            producer.send('global-model', value=global_model)
            print(f"✅ MODÈLE GLOBAL: w1={global_weights['w1']:.3f}, w2={global_weights['w2']:.3f}, w3={global_weights['w3']:.3f}")
            print("=" * 60)
            
            weights_buffer.clear()

except KeyboardInterrupt:
    print("\n🛑 Agrégateur arrêté")
finally:
    consumer.close()
    producer.close()