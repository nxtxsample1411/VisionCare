# VisionCare - Eye Disease Detection Backend

## Overview
Simple Flask backend for eye disease prediction using the trained model.

## Files
- `app.py` - Main Flask backend server
- `eye_disease_model.h5` - Trained model (already exists)
- `requirements.txt` - Python dependencies
- `test_prediction.py` - Test script

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Backend
```bash
python app.py
```

The server will start at: `http://localhost:5000`

## API Endpoints

### POST /predict
Upload an eye image and get disease prediction.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: image file with key "image"

**Response:**
```json
{
  "disease": "normal_eyes",
  "confidence": 0.95
}
```

**Possible disease values:**
- `bulging_eyes`
- `cataracts`
- `crossed_eyes`
- `normal_eyes`
- `uveitis`

### GET /health
Check if backend is running.

**Response:**
```json
{
  "status": "ok",
  "message": "VisionCare backend is running"
}
```

## Testing

### Option 1: Using the test script
```bash
python test_prediction.py
```

### Option 2: Using curl
```bash
curl -X POST -F "image=@path/to/your/image.jpg" http://localhost:5000/predict
```

### Option 3: Using Postman
1. Open Postman
2. Create POST request to `http://localhost:5000/predict`
3. In Body tab, select "form-data"
4. Add key "image" with type "File"
5. Upload an eye image
6. Send request

## Integration with Frontend

### JavaScript Example
```javascript
async function predictDisease(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    console.log('Disease:', result.disease);
    console.log('Confidence:', result.confidence);
}
```

## Notes
- Model accuracy: ~92%
- Image preprocessing: 224x224, normalized to [0,1]
- CORS enabled for frontend integration
- Model loads once at startup for fast predictions
