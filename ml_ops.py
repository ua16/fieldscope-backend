import cv2
from tensorflow.keras.models import load_model
import numpy as np
import os 

def predict_img(image_path, model):
    """Predict using an image path with proper error handling"""
    try:
        # Verify image exists
        if not os.path.exists(image_path):
            raise ValueError(f"Image file not found: {image_path}")

        # Read image
        test_img = cv2.imread(image_path)
        if test_img is None:
            raise ValueError(f"OpenCV could not read image at {image_path}")

        # Verify image is valid
        if test_img.size == 0:
            raise ValueError("Image is empty")

        # Process image
        test_img = cv2.resize(test_img, (224, 224))
        test_img = np.expand_dims(test_img, axis=0)
        result = model["model"].predict(test_img)
        return model["class_names"][np.argmax(result)]

    except Exception as e:
        raise ValueError(f"Prediction failed: {str(e)}")


function_mappings = {
        "predict_img" : predict_img
        }


available_models = {
        # All the models get stored in this for now
        # In the future this should migrate to loading from json
        "SickleCell" : {
            "class_names" : {0 : "Negative", 1 : "Positive"},
            "type" : "CNN-binary-Classification",
            "model_path" : "./models/SickleCell.keras",
            "description" : "A Binary Classification CNN Model to diagnose sickle cell anameia from pictures of cells",
            "function" : "predict_img",
            }
        }


def load_new_model(in_dict: dict, name: str) -> dict:
    # Get the absolute path to the model file
    model_path = os.path.join(os.path.dirname(__file__), "SickleCell.keras")
    
    # Verify the file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    
    # Load the model
    in_dict[name]["model"] = load_model(model_path)
    return in_dict

