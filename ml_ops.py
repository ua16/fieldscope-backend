import cv2
from tensorflow.keras.models import load_model
import numpy as np

def predict_img(image, model):
    test_img=cv2.imread(image)
    test_img=cv2.resize(test_img,(224,224))
    test_img=np.expand_dims(test_img,axis=0)
    result = model.predict(test_img)
    r=np.argmax(result)
    return class_names[r]


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


def load_new_model(in_dict : dict, name : str) -> dict:
    in_dict[name]["model"] = load_model(in_dict[name]["model_path"])
    return in_dict


