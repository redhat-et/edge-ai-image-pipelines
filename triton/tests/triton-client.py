import sys
from ultralytics import YOLO

model = YOLO("http://localhost:8000/yolo", task="detect")
result = model(sys.argv[1])

print(output)
