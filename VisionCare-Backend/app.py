import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Load the trained model using an absolute path to avoid issues with different working directories
BASENAME = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASENAME, 'eye_disease_model.h5')
model = keras.models.load_model(MODEL_PATH)

# Class names in the SAME order as training
CLASS_NAMES = ['bulging_eyes', 'cataracts', 'crossed_eyes', 'normal_eyes', 'uveitis']

def preprocess_image(image_file):
    """
    Preprocess the uploaded image exactly as during training
    """
    # Read image
    img = Image.open(io.BytesIO(image_file.read()))
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize to 224x224
    img = img.resize((224, 224))
    
    # Convert to numpy array
    img_array = np.array(img)
    
    # Normalize pixel values to [0, 1]
    img_array = img_array / 255.0
    
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint to predict eye disease from uploaded image
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        
        # Check if file is empty
        if image_file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Preprocess the image
        processed_image = preprocess_image(image_file)
        
        # Make prediction
        predictions = model.predict(processed_image)
        
        # Get the predicted class index
        predicted_index = np.argmax(predictions[0])
        
        # Get the predicted disease name
        predicted_disease = CLASS_NAMES[predicted_index]
        
        # Get confidence score
        confidence = float(predictions[0][predicted_index])
        
        # Return the result
        return jsonify({
            'disease': predicted_disease,
            'confidence': confidence
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({'status': 'ok', 'message': 'VisionCare backend is running'})

if __name__ == '__main__':
    print("Loading model...")
    print("Model loaded successfully!")
    print("VisionCare backend is ready!")
    app.run(debug=True, host='0.0.0.0', port=5001)
