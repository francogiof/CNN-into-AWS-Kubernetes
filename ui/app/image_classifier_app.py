from typing import Optional

import requests
import streamlit as st
from app.settings import API_BASE_URL
from PIL import Image
from app.utils.browser import save_to_local_storage


import time
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def login(username: str, password: str) -> Optional[str]:
    """This function calls the login endpoint of the API to authenticate the user
    and get a token.

    Args:
        username (str): email of the user
        password (str): password of the user

    Returns:
        Optional[str]: token if login is successful, None otherwise
    """

    url = f"{API_BASE_URL}/login"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }

    response = requests.post(url, headers=headers, data=data)

    logger.info(f"Login response: {response.status_code} - {response.text}")


    if response.status_code == 200:
        token = response.json().get("access_token")
        logger.info(f"Token: {token}")
        return token

    # TODO: Implement the login function
    # Steps to Build the `login` Function:
    # [ ] Construct the API endpoint URL using `API_BASE_URL` and `/login`.
    # [ ] Set up the request headers with `accept: application/json` and
    #     `Content-Type: application/x-www-form-urlencoded`.
    # [ ] Prepare the data payload with fields: `grant_type`, `username`, `password`,
    #     `scope`, `client_id`, and `client_secret`.
    # [ ] Use `requests.post()` to send the API request with the URL, headers,
    #     and data payload.
    # [ ] Check if the response status code is `200`.
    # [ ] If successful, extract the token from the JSON response.
    # [ ] Return the token if login is successful, otherwise return `None`.
    # [ ] Test the function with various inputs.

    return None


def predict(token: str, uploaded_file: Image) -> requests.Response:
    """This function calls the predict endpoint of the API to classify the uploaded
    image.

    Args:
        token (str): token to authenticate the user
        uploaded_file (Image): image to classify

    Returns:
        requests.Response: response from the API
    """
    # TODO: Implement the predict function
    # Steps to Build the `predict` Function:

    url = f"{API_BASE_URL}/model/predict"
    # [ ] Create a dictionary with the file data. The file should be a
    #        tuple with the file name and the file content.
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue())
    }
    # [ ] Add the token to the headers.
    headers = {
        "Authorization": f"Bearer {token}"
    }
    # [ ] Make a POST request to the predict endpoint.
    try: 
        response = requests.post(url, headers=headers, files=files)
    except requests.RequestException as e:
        logger.error(f"Error during prediction: {e}")
        st.error("An error occurred while making the prediction.")
        response = None

    # [ ] Return the response.

    return response


def send_feedback(
    token: str, feedback: str, score: float, prediction: str, image_file_name: str
) -> requests.Response:
    """This function calls the feedback endpoint of the API to send feedback about
    the classification.

    Args:
        token (str): token to authenticate the user
        feedback (str): string with feedback
        score (float): confidence score of the prediction
        prediction (str): predicted class
        image_file_name (str): name of the image file

    Returns:
        requests.Response: response from the API
    """
    url = f"{API_BASE_URL}/feedback"
    
    # Create payload with feedback data
    payload = {
        "feedback": feedback,
        "score": score,
        "predicted_class": prediction,
        "image_file_name": image_file_name
    }
    
    # Add token to headers
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        # Make POST request to feedback endpoint
        response = requests.post(url, json=payload, headers=headers)
        logger.info(f"Feedback response: {response.status_code} - {response.text}")
        return response
    except requests.RequestException as e:
        logger.error(f"Error sending feedback: {e}")
        st.error("An error occurred while sending feedback.")
        return None


# Interfaz de usuario
st.set_page_config(page_title="Image Classifier", page_icon="📷")
st.markdown(
    "<h1 style='text-align: center; color: #4B89DC;'>Image Classifier</h1>",
    unsafe_allow_html=True,
)

# Formulario de login
if "token" not in st.session_state:
    st.markdown("## Login")
    username = st.text_input("Username", value="admin@example.com")
    password = st.text_input("Password", type="password", value="admin"),
    if st.button("Login"):
        token = login(username, password)
        if token:
            st.session_state.token = token
            
            save_to_local_storage("access_token", token)
            st.success("Login successful!")

            time.sleep(0.5)  
            st.rerun()
        else:
            st.error("Login failed. Please check your credentials.")
else:
    st.success("You are logged in!")


if "token" in st.session_state:
    token = st.session_state.token

    # Cargar imagen
    uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

    print(type(uploaded_file))

    # Mostrar imagen escalada si se ha cargado
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen subida", width=300)

    if "classification_done" not in st.session_state:
        st.session_state.classification_done = False

    # Botón de clasificación
    if st.button("Classify"):
        if uploaded_file is not None:
            response = predict(token, uploaded_file)
            if response.status_code == 200:
                result = response.json()
                st.write(f"**Prediction:** {result['prediction']}")
                st.write(f"**Score:** {result['score']}")
                st.session_state.classification_done = True
                st.session_state.result = result
            else:
                st.error("Error classifying image. Please try again.")
        else:
            st.warning("Please upload an image before classifying.")

    # Mostrar campo de feedback solo si se ha clasificado la imagen
    if st.session_state.classification_done:
        st.markdown("## Feedback")
        feedback = st.text_area("If the prediction was wrong, please provide feedback.")
        if st.button("Send Feedback"):
            if feedback:
                token = st.session_state.token
                result = st.session_state.result
                score = result["score"]
                prediction = result["prediction"]
                image_file_name = result.get("image_file_name", "uploaded_image")
                response = send_feedback(
                    token, feedback, score, prediction, image_file_name
                )
                if response and response.status_code == 201:
                    st.success("Thanks for your feedback!")
                else:
                    st.error("Error sending feedback. Please try again.")
            else:
                st.warning("Please provide feedback before sending.")

    # Pie de página
    st.markdown("<hr style='border:2px solid #4B89DC;'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #4B89DC;'>2024 Image Classifier App</p>",
        unsafe_allow_html=True,
    )
