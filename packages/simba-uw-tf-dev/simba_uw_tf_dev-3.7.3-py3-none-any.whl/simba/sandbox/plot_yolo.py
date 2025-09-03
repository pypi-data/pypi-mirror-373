import os

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
from ultralytics import YOLO
model = YOLO(r"D:\cvat_annotations\yolo_07032025\mdl\train\args.yaml", task='pose')
model.show()