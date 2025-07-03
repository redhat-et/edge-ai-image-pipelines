import numpy as np
from PIL import Image
import io
import tritonclient.http as httpclient
import requests

url = "https://cataas.com/cat?width=640&height=640"
response = requests.get(url)

# Use Pillow instead of cv2
img = Image.open(io.BytesIO(response.content))
img = img.convert('RGB')  # Ensure RGB format
img = np.array(img)  # Convert PIL Image to numpy array

img = img.transpose(2, 0, 1)  # HWC -> CHW
img = img.astype(np.float32) / 255.0
img = np.expand_dims(img, axis=0)  # Add batch dim

client = httpclient.InferenceServerClient(url="server:8000")

inputs = [httpclient.InferInput("images", img.shape, "FP32")]
inputs[0].set_data_from_numpy(img)
outputs = [httpclient.InferRequestedOutput("output0")]

response = client.infer(model_name="model", inputs=inputs, outputs=outputs)
output = response.as_numpy("output0")
print(output)
