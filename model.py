# model.py - Train or load the machine learning model for failure prediction

import numpy as np
from sklearn.ensemble import RandomForestClassifier
# Optionally, we could use joblib to save/load the model if we wanted persistence:
# from joblib import dump, load

# Import configuration thresholds and labels
import config

def generate_training_data(n_samples=5000):
    """
    Generate synthetic training data for the predictive maintenance model.
    Returns (X, y) where X is a numpy array of shape (n_samples, 4) with features:
    [temperature, vibration, pressure, cycles], and y is an array of labels (0,1,2).
    """
    X = []
    y = []
    # Helper function to label a data point based on thresholds
    def label_point(temp, vib, press, cycles):
        # Failure criteria (class 2)
        if (temp >= config.TEMP_FAIL or vib >= config.VIB_FAIL or 
            press <= config.PRESS_FAIL_LOW or press >= config.PRESS_FAIL_HIGH or 
            cycles >= config.CYCLES_FAIL):
            return 2  # Failure Predicted
        # Warning criteria (class 1)
        if (temp >= config.TEMP_WARN or vib >= config.VIB_WARN or 
            press <= config.PRESS_WARN_LOW or press >= config.PRESS_WARN_HIGH or 
            cycles >= config.CYCLES_WARN):
            return 1  # Warning
        # Otherwise normal (class 0)
        return 0

    for _ in range(n_samples):
        # Randomly sample within a broad range for each parameter
        temp = np.random.uniform(50, 120)      # temperature in °C
        vib = np.random.uniform(0, 20)         # vibration in mm/s
        press = np.random.uniform(70, 180)     # pressure in bar
        cycles = np.random.uniform(0, 1500)    # cycle count
        # Determine label based on thresholds
        label = label_point(temp, vib, press, cycles)
        # To ensure we have enough examples of warning and failure, 
        # we can resample or adjust probabilities (optional).
        X.append([temp, vib, press, cycles])
        y.append(label)
    X = np.array(X, dtype=float)
    y = np.array(y, dtype=int)
    return X, y

def train_model():
    """
    Train the Random Forest model on synthetic data. 
    Returns the trained model.
    """
    # Generate training dataset
    X_train, y_train = generate_training_data(n_samples=5000)
    # Initialize Random Forest classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    return clf

# If we wanted to save the model to disk for reuse (not strictly necessary here):
# model = train_model()
# dump(model, "maintenance_model.joblib")
# Then in future runs, load with load("maintenance_model.joblib") instead of training again.

# For this project, we'll train fresh each run for simplicity.
if __name__ == "__main__":
    # Simple test: train and output feature importance
    model = train_model()
    print("Feature importances:", model.feature_importances_)
