import requests

# Test the backend prediction endpoint
def test_prediction(image_path):
    """
    Test the prediction endpoint with an image
    """
    url = 'http://localhost:5000/predict'
    
    # Open and send the image
    with open(image_path, 'rb') as img_file:
        files = {'image': img_file}
        response = requests.post(url, files=files)
    
    # Print the result
    if response.status_code == 200:
        result = response.json()
        print(f"Predicted Disease: {result['disease']}")
        print(f"Confidence: {result['confidence']:.2%}")
    else:
        print(f"Error: {response.json()}")

if __name__ == '__main__':
    # Example: Test with an image from the test dataset
    test_image = 'dataset/test/0001_0P_0H_0V_png_jpg.rf.30af7b94aec11fcb4a5d2f76d0903a2b.jpg'
    
    print("Testing VisionCare prediction...")
    test_prediction(test_image)
