import streamlit as st
import openai
import base64
from ultralytics import YOLO
from PIL import Image

# Set the title for the Streamlit app
st.title("Triton Server Demo App")

# Create a text area for user input
image = st.file_uploader("Upload a 640x640 JPEG:", type=["jpg","jpeg"])

model = YOLO("http://localhost:8000/yolo11x", task="detect")

if st.button("Process Image"):
    if image: 
        with st.spinner("Generating..."):
            image = Image.open(image)
            result = model.predict(image)[0]
        result.save("detect.jpg")

        # Display the model's response
        st.write("### Processed Image")
        st.image("detect.jpg")
