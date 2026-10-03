import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler

class PageReplacementPredictor:
    """
    ML model for predicting the best page replacement algorithm.
    """
    def __init__(self):
        """Initialize the predictor."""
        self.model = DecisionTreeClassifier(max_depth=5)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def preprocess_features(self, features_list):
        """
        Preprocess features for the model.
        
        Args:
            features_list: List of feature dictionaries
            
        Returns:
            Numpy array of preprocessed features
        """
        # Convert list of dictionaries to array
        feature_names = list(features_list[0].keys())
        X = np.array([[features[name] for name in feature_names] for features in features_list])
        
        # Scale features
        if not self.is_trained:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        return X_scaled, feature_names
    
    def train(self, features_list, labels):
        """
        Train the model with labeled data.
        
        Args:
            features_list: List of feature dictionaries
            labels: List of corresponding labels
            
        Returns:
            Accuracy score
        """
        # Preprocess features
        X, feature_names = self.preprocess_features(features_list)
        y = np.array(labels)
        
        # Train the model
        self.model.fit(X, y)
        self.is_trained = True
        
        # Evaluate on training data
        predictions = self.model.predict(X)
        accuracy = np.mean(predictions == y)
        
        return accuracy
    
    def predict(self, features):
        """
        Predict the best algorithm for the given features.
        
        Args:
            features: Dictionary of features
            
        Returns:
            Predicted best algorithm
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained yet")
        
        X, _ = self.preprocess_features([features])
        return self.model.predict(X)[0]
    
    def feature_importance(self):
        """
        Get feature importance from the model.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained yet")
        
        # Make sure the scaler has been fitted
        if not hasattr(self.scaler, 'feature_names_in_'):
            # If feature_names_in_ is not available, we need to handle this differently
            # This could happen if the scaler hasn't been properly fitted
            # Let's use generic feature names as a fallback
            feature_count = len(self.model.feature_importances_)
            feature_names = [f"feature_{i}" for i in range(feature_count)]
        else:
            feature_names = list(self.scaler.feature_names_in_)
        importance = self.model.feature_importances_
        
        return dict(zip(feature_names, importance))