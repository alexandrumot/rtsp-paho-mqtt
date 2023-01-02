# Script that fetches video using OpenCV from RTSP IP CAMERA via URL ex. "rtsp://192.168.0.178:5554" and then converts it to bytes to publish it to specified topic on HiveMQ Cloud (or other mqtt cloud provider) via paho-MQTT. 

import paho.mqtt.client as paho
from paho import mqtt
import base64
import time
import cv2
import os
from dotenv import load_dotenv

load_dotenv()

# Fill these |  |  |
#            V  V  V
CLOUD_USERNAME = os.getenv("CLOUD_USERNAME")
CLOUD_PASSWORD = os.getenv("CLOUD_PASSWORD")
CLOUD_BROKER = os.getenv("CLOUD_BROKER")

TOPIC = "camera/video"

client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5) # You can change the protocol to the mqtt version you're using
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS) # Minimum level of security, no certificate, no key
client.username_pw_set(CLOUD_USERNAME, CLOUD_PASSWORD) # Username and Password you created on cloud
client.connect(CLOUD_BROKER, 1883)

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0" # Get rid of some possible errors
cap = cv2.VideoCapture("rtsp://192.168.0.178:5554/out.h264") # <- Here goes your own local ip camera.

try:
  while(1):
    start = time.time()
    _, frame = cap.read()
    _, buffer = cv2.imencode(".jpg", frame)
    jpg_as_text = base64.b64encode(buffer) # Convert image to bytes
    client.publish(TOPIC, jpg_as_text) # Send bytes through publish method
    
    end = time.time() # This helps determining the framerate of the camera and at which you publish 
    t = end - start # I recommend reducing the framerate so you don't produce too much traffic on the cloud
    fps = 1/t
    print(fps)
except:
  cap.release()
  client.disconnect()