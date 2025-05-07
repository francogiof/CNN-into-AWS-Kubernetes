import json
import os
import time

import numpy as np
import redis
import settings
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image

import logging
logging.basicConfig(level=logging.INFO)
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
db = redis.StrictRedis(
    host=settings.REDIS_IP,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB_ID,
    decode_responses=True
)

# TODO
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
model = ResNet50(weights="imagenet")


def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
     # Ruta de la imagen
    image_path = os.path.join(settings.UPLOAD_FOLDER, image_name)

    # check if image exists
    if not os.path.exists(image_path):
        print(f"Image {image_name} not found in {settings.UPLOAD_FOLDER}")
        return None, None

    # Cargar y preprocesar la imagen
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # Realizar predicción
    predictions = model.predict(img_array)
    decoded_predictions = decode_predictions(predictions, top=1)[0][0]

    # Obtener clase y probabilidad
    class_name = decoded_predictions[1]
    pred_probability = round(float(decoded_predictions[2]), 4)

    return class_name, pred_probability


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        # Obtener un nuevo trabajo desde Redis
        job_data = db.brpop(settings.REDIS_QUEUE)
        if job_data is None:
            logging.info("No job found, sleeping...")
            print("No job found, sleeping...")
            time.sleep(settings.SERVER_SLEEP)
            continue

        # Decodificar datos del trabajo
        _ , job_payload = job_data
        job_payload = json.loads(job_payload)

        job_id = job_payload.get("id")  # Obtener el ID real del trabajo de los datos
        if not job_id:
            print("No job ID found in payload, skipping...")
            continue

        # Obtener el nombre de la imagen
        image_name = job_payload.get("image_name")
        if not image_name:
            continue

        # Realizar predicción
        class_name, pred_probability = predict(image_name)

        # Preparar resultados
        output = {
            "prediction": class_name,
            "score": pred_probability
        }

        # Almacenar resultados en Redis
        db.set(job_id, json.dumps(output))

        # Dormir un poco antes de la siguiente iteración
        time.sleep(settings.SERVER_SLEEP)



if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
