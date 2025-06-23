import numpy as np
import cv2
import tritonclient.http as httpclient
import requests

url = "https://cataas.com/cat?width=640&height=640"
response = requests.get(url)
img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img = img.transpose(2, 0, 1)  # HWC -> CHW
img = img.astype(np.float32) / 255.0
img = np.expand_dims(img, axis=0)  # Add batch dim

client = httpclient.InferenceServerClient(url="tis-server:8000")

inputs = [httpclient.InferInput("images", img.shape, "FP32")]
inputs[0].set_data_from_numpy(img)
outputs = [httpclient.InferRequestedOutput("output0")]

response = client.infer(model_name="yolo", inputs=inputs, outputs=outputs)
output = response.as_numpy("output0")
print(output[0][0][0])
