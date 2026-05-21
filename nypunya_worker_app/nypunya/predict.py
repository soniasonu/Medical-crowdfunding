import tensorflow as tf
import numpy as np
import json
from tensorflow.keras.preprocessing import image

model = tf.keras.models.load_model('problem_detector_model.h5')

with open('labels.json') as f:
    class_indices = json.load(f)

labels = {v: k for k, v in class_indices.items()}

THRESHOLD = 0.7

def predict_problem(img_path):
    img = image.load_img(img_path, target_size=(150,150))
    img_array = image.img_to_array(img)/255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array)

    confidence = np.max(predictions)
    index = np.argmax(predictions)

    if confidence < THRESHOLD:
        return "unknown", confidence

    return labels[index], confidence


if __name__ == '__main__':
    result, conf = predict_problem('test_images/w1.jpg')
    print('Detected Problem:', result)
    print('Confidence:', conf)