import numpy as np

class SimpleAnomalyDetector:
    """
    Modèle simple: Régression Logistique avec SGD
    """
    def __init__(self, n_features=3):
        # Initialise les poids aléatoirement
        self.weights = np.random.randn(n_features)
        self.bias = 0.0
        self.learning_rate = 0.01
    
    def predict(self, X):
        """Prédiction: 1 si anomalie, 0 sinon"""
        z = np.dot(X, self.weights) + self.bias
        return 1 / (1 + np.exp(-z))  # Sigmoid
    
    def train_step(self, X, y):
        """
        Un pas de Stochastic Gradient Descent (SGD)
        """
        # Prédiction
        y_pred = self.predict(X)
        
        # Calcul du gradient
        error = y_pred - y
        grad_w = X * error
        grad_b = error
        
        # Mise à jour des poids
        self.weights -= self.learning_rate * grad_w
        self.bias -= self.learning_rate * grad_b
        
        # Calcul de la perte (loss)
        loss = -y * np.log(y_pred + 1e-10) - (1-y) * np.log(1-y_pred + 1e-10)
        return loss
    
    def get_weights(self):
        """Retourne les poids pour l'agrégation"""
        return {
            'weights': self.weights.tolist(),
            'bias': float(self.bias)
        }
    
    def set_weights(self, weights_dict):
        """Met à jour les poids depuis l'agrégateur"""
        self.weights = np.array(weights_dict['weights'])
        self.bias = weights_dict['bias']