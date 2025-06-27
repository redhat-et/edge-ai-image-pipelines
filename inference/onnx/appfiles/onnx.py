import onnxruntime as ort
import numpy as np
import cv2
# Load the ONNX model
session = ort.InferenceSession("/share/yolo11n.onnx", providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])

# Load and preprocess the image
image = cv2.imread("/share/cat.jpg")
if image is None:
    raise ValueError("Could not load image cat.jpg")

# Get input details from the model
input_name = session.get_inputs()[0].name
input_shape = session.get_inputs()[0].shape
height, width = input_shape[2], input_shape[3]

# Preprocess image to BCHW format
image = cv2.resize(image, (width, height))
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image = image.transpose(2, 0, 1)  # HWC to CHW
image = image.astype(np.float32) / 255.0  # Normalize to [0,1]
image = np.expand_dims(image, axis=0)  # Add batch dimension (BCHW)

# Run inference
outputs = session.run(None, {input_name: image})
print("Model output shape:", [output.shape for output in outputs])


