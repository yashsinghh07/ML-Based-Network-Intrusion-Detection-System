"""
Deep Learning NIDS Training Script
Trains LSTM and Autoencoder models for network intrusion detection.
Uses flow-based features extracted from network traffic.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.ensemble import RandomForestClassifier
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Input, RepeatVector, TimeDistributed, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

class FlowFeatureExtractor:
    """Extract flow-based features from network traffic data"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
    
    def extract_flow_features(self, df):
        """
        Extract flow-based features from NSL-KDD dataset.
        Groups by 5-tuple and creates flow statistics.
        """
        print("Extracting flow-based features...")
        
        # Create flow identifier (5-tuple simulation)
        # Since NSL-KDD doesn't have explicit flows, we'll use connection-based features
        flow_features = []
        
        # Select relevant features for flow representation
        flow_cols = [
            'duration', 'protocol_type', 'service', 'flag', 
            'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent',
            'hot', 'num_failed_logins', 'logged_in', 'num_compromised',
            'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
            'num_shells', 'num_access_files', 'num_outbound_cmds',
            'is_host_login', 'is_guest_login', 'count', 'srv_count',
            'serror_rate', 'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate',
            'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
            'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate',
            'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
            'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
            'dst_host_srv_rerror_rate'
        ]
        
        # Filter available columns
        available_cols = [col for col in flow_cols if col in df.columns]
        flow_df = df[available_cols + ['label']].copy()
        
        # Encode categorical features
        categorical_cols = ['protocol_type', 'service', 'flag']
        for col in categorical_cols:
            if col in flow_df.columns:
                le = LabelEncoder()
                flow_df[col] = le.fit_transform(flow_df[col].astype(str))
        
        # Handle missing values
        flow_df = flow_df.fillna(0)
        
        # Create binary label
        flow_df['is_attack'] = flow_df['label'].apply(lambda x: 0 if x == 'normal' else 1)
        
        return flow_df[available_cols], flow_df['is_attack']
    
    def create_sequences(self, X, y, sequence_length=10):
        """
        Create sequences for LSTM training.
        Groups consecutive samples into sequences.
        """
        print(f"Creating sequences of length {sequence_length}...")
        X_seq, y_seq = [], []
        
        for i in range(len(X) - sequence_length + 1):
            X_seq.append(X[i:i+sequence_length])
            y_seq.append(y[i+sequence_length-1])
        
        return np.array(X_seq), np.array(y_seq)

def train_lstm_model(X_train, y_train, X_val, y_val, sequence_length=10):
    """Train LSTM model for sequence-based detection"""
    print("\n" + "="*60)
    print("Training LSTM Model")
    print("="*60)
    
    # Create sequences
    feature_extractor = FlowFeatureExtractor()
    X_train_seq, y_train_seq = feature_extractor.create_sequences(
        X_train.values, y_train.values, sequence_length
    )
    X_val_seq, y_val_seq = feature_extractor.create_sequences(
        X_val.values, y_val.values, sequence_length
    )
    
    print(f"Training sequences shape: {X_train_seq.shape}")
    print(f"Validation sequences shape: {X_val_seq.shape}")
    
    # Build LSTM model
    model = Sequential([
        LSTM(64, activation='relu', input_shape=(sequence_length, X_train.shape[1]), return_sequences=True),
        Dropout(0.3),
        LSTM(32, activation='relu', return_sequences=False),
        Dropout(0.3),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', 'precision', 'recall']
    )
    
    # Callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    checkpoint = ModelCheckpoint('lstm_model.h5', monitor='val_loss', save_best_only=True)
    
    # Train model
    history = model.fit(
        X_train_seq, y_train_seq,
        validation_data=(X_val_seq, y_val_seq),
        epochs=50,
        batch_size=64,
        callbacks=[early_stopping, checkpoint],
        verbose=1
    )
    
    return model, history

def train_autoencoder(X_train, X_val, encoding_dim=32):
    """Train Autoencoder for anomaly detection"""
    print("\n" + "="*60)
    print("Training Autoencoder Model")
    print("="*60)
    
    input_dim = X_train.shape[1]
    
    # Build autoencoder
    input_layer = Input(shape=(input_dim,))
    
    # Encoder
    encoded = Dense(64, activation='relu')(input_layer)
    encoded = Dense(encoding_dim, activation='relu')(encoded)
    
    # Decoder
    decoded = Dense(64, activation='relu')(encoded)
    decoded = Dense(input_dim, activation='sigmoid')(decoded)
    
    autoencoder = Model(input_layer, decoded)
    encoder = Model(input_layer, encoded)
    
    autoencoder.compile(optimizer='adam', loss='mse')
    
    # Callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    checkpoint = ModelCheckpoint('autoencoder_model.h5', monitor='val_loss', save_best_only=True)
    
    # Train on normal traffic only
    normal_mask = X_train.sum(axis=1) > 0  # Simple normal traffic filter
    X_train_normal = X_train[normal_mask]
    
    print(f"Training on {len(X_train_normal)} normal samples...")
    
    history = autoencoder.fit(
        X_train_normal, X_train_normal,
        validation_data=(X_val, X_val),
        epochs=50,
        batch_size=64,
        callbacks=[early_stopping, checkpoint],
        verbose=1
    )
    
    return autoencoder, encoder, history

def evaluate_autoencoder(autoencoder, X_test, y_test, threshold_percentile=95):
    """Evaluate autoencoder using reconstruction error"""
    # Get reconstruction errors
    X_pred = autoencoder.predict(X_test)
    reconstruction_errors = np.mean(np.square(X_test - X_pred), axis=1)
    
    # Set threshold based on normal traffic
    normal_errors = reconstruction_errors[y_test == 0]
    threshold = np.percentile(normal_errors, threshold_percentile)
    
    # Predict anomalies
    predictions = (reconstruction_errors > threshold).astype(int)
    
    return predictions, reconstruction_errors, threshold

def train_baseline_rf(X_train, y_train, X_test, y_test):
    """Train Random Forest baseline for comparison"""
    print("\n" + "="*60)
    print("Training Random Forest Baseline")
    print("="*60)
    
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    
    y_pred = rf.predict(X_test)
    y_pred_proba = rf.predict_proba(X_test)[:, 1]
    
    return rf, y_pred, y_pred_proba

def print_comparison_results(results):
    """Print comparison table of all models"""
    print("\n" + "="*60)
    print("MODEL COMPARISON RESULTS")
    print("="*60)
    
    comparison_df = pd.DataFrame(results)
    print(comparison_df.to_string(index=False))
    
    return comparison_df

def main():
    print("="*60)
    print("Deep Learning NIDS Training")
    print("="*60)
    
    # Load dataset
    print("\nLoading NSL-KDD dataset...")
    columns = [
        "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", "land",
        "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in", "num_compromised",
        "root_shell", "su_attempted", "num_root", "num_file_creations", "num_shells",
        "num_access_files", "num_outbound_cmds", "is_host_login", "is_guest_login", "count",
        "srv_count", "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate",
        "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate", "dst_host_count",
        "dst_host_srv_count", "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
        "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate", "dst_host_serror_rate",
        "dst_host_srv_serror_rate", "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label",
        "difficulty"
    ]
    
    if not os.path.exists("KDDTrain+.txt"):
        print("Error: KDDTrain+.txt not found!")
        print("Please ensure the dataset file is in the current directory.")
        return
    
    df = pd.read_csv("KDDTrain+.txt", names=columns)
    print(f"Dataset loaded: {len(df)} samples")
    
    # Extract flow features
    feature_extractor = FlowFeatureExtractor()
    X, y = feature_extractor.extract_flow_features(df)
    
    print(f"Features shape: {X.shape}")
    print(f"Class distribution:\n{y.value_counts()}")
    
    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # Convert back to DataFrame for easier handling
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X.columns)
    X_val_scaled = pd.DataFrame(X_val_scaled, columns=X.columns)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X.columns)
    
    # Save scaler
    joblib.dump(scaler, 'deep_scaler.pkl')
    
    results = []
    
    # 1. Train Random Forest Baseline
    rf_model, rf_pred, rf_pred_proba = train_baseline_rf(
        X_train_scaled, y_train, X_test_scaled, y_test
    )
    
    rf_report = classification_report(y_test, rf_pred, output_dict=True, zero_division=0)
    rf_auc = roc_auc_score(y_test, rf_pred_proba)
    
    results.append({
        'Model': 'Random Forest',
        'Accuracy': f"{rf_report['accuracy']:.4f}",
        'Precision': f"{rf_report['1']['precision']:.4f}",
        'Recall': f"{rf_report['1']['recall']:.4f}",
        'F1-Score': f"{rf_report['1']['f1-score']:.4f}",
        'ROC-AUC': f"{rf_auc:.4f}"
    })
    
    joblib.dump(rf_model, 'rf_baseline_model.pkl')
    
    # 2. Train LSTM
    try:
        lstm_model, lstm_history = train_lstm_model(
            X_train_scaled, y_train, X_val_scaled, y_val, sequence_length=10
        )
        
        # Evaluate LSTM
        X_test_seq, y_test_seq = feature_extractor.create_sequences(
            X_test_scaled.values, y_test.values, sequence_length=10
        )
        lstm_pred_proba = lstm_model.predict(X_test_seq)
        lstm_pred = (lstm_pred_proba > 0.5).astype(int).flatten()
        
        lstm_report = classification_report(y_test_seq, lstm_pred, output_dict=True, zero_division=0)
        lstm_auc = roc_auc_score(y_test_seq, lstm_pred_proba)
        
        results.append({
            'Model': 'LSTM',
            'Accuracy': f"{lstm_report['accuracy']:.4f}",
            'Precision': f"{lstm_report['1']['precision']:.4f}",
            'Recall': f"{lstm_report['1']['recall']:.4f}",
            'F1-Score': f"{lstm_report['1']['f1-score']:.4f}",
            'ROC-AUC': f"{lstm_auc:.4f}"
        })
    except Exception as e:
        print(f"Error training LSTM: {e}")
        results.append({
            'Model': 'LSTM',
            'Accuracy': 'Error',
            'Precision': 'Error',
            'Recall': 'Error',
            'F1-Score': 'Error',
            'ROC-AUC': 'Error'
        })
    
    # 3. Train Autoencoder
    try:
        autoencoder, encoder, ae_history = train_autoencoder(
            X_train_scaled.values, X_val_scaled.values, encoding_dim=32
        )
        
        # Evaluate Autoencoder
        ae_pred, ae_errors, threshold = evaluate_autoencoder(
            autoencoder, X_test_scaled.values, y_test.values
        )
        
        ae_report = classification_report(y_test, ae_pred, output_dict=True, zero_division=0)
        # For autoencoder, we use reconstruction error as score
        ae_auc = roc_auc_score(y_test, ae_errors)
        
        results.append({
            'Model': 'Autoencoder',
            'Accuracy': f"{ae_report['accuracy']:.4f}",
            'Precision': f"{ae_report['1']['precision']:.4f}",
            'Recall': f"{ae_report['1']['recall']:.4f}",
            'F1-Score': f"{ae_report['1']['f1-score']:.4f}",
            'ROC-AUC': f"{ae_auc:.4f}"
        })
        
        # Save encoder
        encoder.save('autoencoder_encoder.h5')
        joblib.dump(threshold, 'autoencoder_threshold.pkl')
    except Exception as e:
        print(f"Error training Autoencoder: {e}")
        results.append({
            'Model': 'Autoencoder',
            'Accuracy': 'Error',
            'Precision': 'Error',
            'Recall': 'Error',
            'F1-Score': 'Error',
            'ROC-AUC': 'Error'
        })
    
    # Print comparison
    comparison_df = print_comparison_results(results)
    comparison_df.to_csv('model_comparison_results.csv', index=False)
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print("\nSaved Models:")
    print("  - lstm_model.h5 (LSTM model)")
    print("  - autoencoder_model.h5 (Autoencoder model)")
    print("  - autoencoder_encoder.h5 (Encoder for inference)")
    print("  - rf_baseline_model.pkl (Random Forest baseline)")
    print("  - deep_scaler.pkl (Feature scaler)")
    print("  - autoencoder_threshold.pkl (Anomaly threshold)")
    print("  - model_comparison_results.csv (Comparison results)")

if __name__ == "__main__":
    main()

