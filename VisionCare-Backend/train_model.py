import os
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 20

# Paths
TRAIN_DIR = 'dataset/train'
VALID_DIR = 'dataset/valid'
TEST_DIR = 'dataset/test'

def load_data(data_dir):
    """Load images and labels from directory using _classes.csv"""
    csv_path = os.path.join(data_dir, '_classes.csv')
    df = pd.read_csv(csv_path)
    
    # Clean column names (remove spaces)
    df.columns = df.columns.str.strip()
    
    # Get disease columns (all except filename)
    disease_cols = [col for col in df.columns if col != 'filename']
    
    images = []
    labels = []
    
    print(f"Loading images from {data_dir}...")
    for idx, row in df.iterrows():
        img_path = os.path.join(data_dir, row['filename'].strip())
        
        if os.path.exists(img_path):
            # Load and preprocess image
            img = load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
            img_array = img_to_array(img) / 255.0  # Normalize
            images.append(img_array)
            
            # Get label (find which disease column has value 1)
            label_values = row[disease_cols].values
            label_idx = np.argmax(label_values)
            labels.append(label_idx)
    
    print(f"Loaded {len(images)} images")
    return np.array(images), np.array(labels), disease_cols

# Load datasets
print("="*50)
print("LOADING TRAINING DATA")
print("="*50)
X_train, y_train, disease_names = load_data(TRAIN_DIR)

print("\n" + "="*50)
print("LOADING VALIDATION DATA")
print("="*50)
X_valid, y_valid, _ = load_data(VALID_DIR)

print("\n" + "="*50)
print("LOADING TEST DATA")
print("="*50)
X_test, y_test, _ = load_data(TEST_DIR)

# Convert labels to categorical
num_classes = len(disease_names)
y_train_cat = to_categorical(y_train, num_classes)
y_valid_cat = to_categorical(y_valid, num_classes)
y_test_cat = to_categorical(y_test, num_classes)

print("\n" + "="*50)
print("DATASET SUMMARY")
print("="*50)
print(f"Training samples: {len(X_train)}")
print(f"Validation samples: {len(X_valid)}")
print(f"Test samples: {len(X_test)}")
print(f"Number of classes: {num_classes}")
print(f"Disease classes: {disease_names}")

# Build CNN model
print("\n" + "="*50)
print("BUILDING MODEL")
print("="*50)

model = Sequential([
    # First Conv Block
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    MaxPooling2D(2, 2),
    
    # Second Conv Block
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    
    # Third Conv Block
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    
    # Fourth Conv Block
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    
    # Flatten and Dense layers
    Flatten(),
    Dense(512, activation='relu'),
    Dropout(0.5),
    Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print(model.summary())

# Train model
print("\n" + "="*50)
print("TRAINING MODEL")
print("="*50)

history = model.fit(
    X_train, y_train_cat,
    validation_data=(X_valid, y_valid_cat),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    verbose=1
)

# Evaluate on test set
print("\n" + "="*50)
print("EVALUATING ON TEST SET")
print("="*50)

test_loss, test_accuracy = model.evaluate(X_test, y_test_cat, verbose=0)
print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f}")

# Save model
model_path = 'eye_disease_model.h5'
model.save(model_path)

print("\n" + "="*50)
print("TRAINING COMPLETE")
print("="*50)
print(f"Model saved as: {model_path}")
print(f"Final Test Accuracy: {test_accuracy*100:.2f}%")
