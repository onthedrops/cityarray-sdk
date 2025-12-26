"""
CITYARRAY Hailo Detector
Uses AI HAT for fast inference
"""

from hailo_platform import HEF, VDevice, InputVStreamParams, OutputVStreamParams, InferVStreams
import numpy as np
from PIL import Image
import subprocess
from datetime import datetime
from pathlib import Path
from database import log_detection

COCO_NAMES = ["person","bicycle","car","motorcycle","airplane","bus","train","truck","boat","traffic light","fire hydrant","stop sign","parking meter","bench","bird","cat","dog","horse","sheep","cow","elephant","bear","zebra","giraffe","backpack","umbrella","handbag","tie","suitcase","frisbee","skis","snowboard","sports ball","kite","baseball bat","baseball glove","skateboard","surfboard","tennis racket","bottle","wine glass","cup","fork","knife","spoon","bowl","banana","apple","sandwich","orange","broccoli","carrot","hot dog","pizza","donut","cake","chair","couch","potted plant","bed","dining table","toilet","tv","laptop","mouse","remote","keyboard","cell phone","microwave","oven","toaster","sink","refrigerator","book","clock","vase","scissors","teddy bear","hair drier","toothbrush"]

IMAGE_DIR = Path.home() / "pi" / "images"
IMAGE_DIR.mkdir(exist_ok=True)

class HailoDetector:
    def __init__(self):
        print("Loading Hailo model...")
        self.hef = HEF("/usr/share/hailo-models/yolov8s_h8l.hef")
        self.device = VDevice()
        self.network_group = self.device.configure(self.hef)[0]
        self.input_params = InputVStreamParams.make(self.network_group)
        self.output_params = OutputVStreamParams.make(self.network_group)
        print("Hailo ready!")
    
    def capture(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = IMAGE_DIR / f"capture_{timestamp}.jpg"
        subprocess.run(["rpicam-still", "-o", str(path), "-t", "500", "--nopreview", "--ev", "1"], capture_output=True)
        return path
    
    def detect(self, image_path, conf_threshold=0.3):
        img = Image.open(image_path).convert("RGB").resize((640, 640))
        input_data = np.array(img, dtype=np.uint8)
        
        with self.network_group.activate():
            with InferVStreams(self.network_group, self.input_params, self.output_params) as pipeline:
                results = pipeline.infer({"yolov8s/input_layer1": np.expand_dims(input_data, axis=0)})
        
        detections = []
        raw = results["yolov8s/yolov8_nms_postprocess"][0]
        
        for class_id, class_dets in enumerate(raw):
            if len(class_dets) > 0:
                for det in class_dets:
                    if len(det) >= 5 and det[4] > conf_threshold:
                        detections.append({
                            "class": COCO_NAMES[class_id],
                            "confidence": float(det[4])
                        })
                        log_detection(COCO_NAMES[class_id], float(det[4]), str(image_path))
        
        return detections
    
    def close(self):
        self.device.release()


if __name__ == "__main__":
    detector = HailoDetector()
    
    print("\nCapturing...")
    img = detector.capture()
    
    print("Detecting...")
    dets = detector.detect(img)
    
    if dets:
        print(f"\nFound {len(dets)} object(s):")
        for d in dets:
            print(f"  {d['class']}: {d['confidence']:.0%}")
    else:
        print("No objects detected")
