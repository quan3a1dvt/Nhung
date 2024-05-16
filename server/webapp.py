
import argparse
import io
from PIL import Image
import datetime

import torch

import cv2
import numpy as np
from re import DEBUG, sub
from flask import Flask, render_template, request, redirect, send_file, url_for, Response
from werkzeug.utils import secure_filename, send_from_directory
import os
import subprocess
from subprocess import Popen
import re
import requests
import shutil
import time
import glob
from flask_cors import CORS
from ultralytics import YOLO
from ultralytics.solutions import object_counter, speed_estimation
from flask_socketio import SocketIO
import base64
import urllib
device = 'cuda' if torch.cuda.is_available() else 'cpu'

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*",port=5000,host='0.0.0.0')
model = None
counter = None
speed_obj = None
url_low = "http://10.0.0.172/cam-lo.jpg"
url_mid = "http://10.0.0.172/cam-mid.jpg"
url_high = "http://10.0.0.172/cam-hi.jpg"


tracked_in = []
tracked_out = []
last_count_in = 0
last_count_out = 0
counted = 0

bus_in = 0
bus_out = 0
car_in = 0
car_out = 0
truck_in = 0
truck_out = 0

stop = False

@app.route("/stop", methods=["POST"])
def stop():
    global stop
    stop = True
    return "Stopped"

@app.route("/esp", methods=["POST"])
def predict_img_esp():
    global stop
    while True:
        if stop:
            stop = False
            break
        frame = urllib.request.urlopen(url_mid)
        img_np = np.array(bytearray(frame.read()), dtype=np.uint8)
        img = cv2.imdecode(img_np, -1)
        detections =  model(img, save=True) 
        _, buffer = cv2.imencode('.jpg', detections[0].plot())
        frame_as_text = base64.b64encode(buffer).decode('utf-8')
        socketio.emit('frame', frame_as_text)
    return "Done"

@app.route("/webcam", methods=["POST"])
def predict_img_webcam():
    global stop
    cam = VideoCapture(0)
    while True:
        if stop:
            stop = False
            break
        result, frame = cam.read() 
        if result:
            detections =  model(frame, save=True) 
            _, buffer = cv2.imencode('.jpg', detections[0].plot())
            frame_as_text = base64.b64encode(buffer).decode('utf-8')
            socketio.emit('frame', frame_as_text)
    return "Done"

@app.route("/upload", methods=["POST"])
def predict_img():
    global stop

    tracked_in = []
    tracked_out = []
    last_count_in = 0
    last_count_out = 0
    counted = 0

    bus_in = 0
    bus_out = 0
    car_in = 0
    car_out = 0
    truck_in = 0
    truck_out = 0
    if 'file' in request.files:
        f = request.files['file']
        basepath = os.path.dirname(__file__)
        filepath = os.path.join(basepath,'uploads',f.filename)
        print("upload folder is ", filepath)
        f.save(filepath)
        global imgpath
        predict_img.imgpath = f.filename
        print("printing predict_img :::::: ", predict_img)                                 
        file_extension = f.filename.rsplit('.', 1)[1].lower() 
        
        if file_extension == 'jpg':
            img = cv2.imread(filepath)

            # Perform the detection

            detections =  model(img, save=True) 
            _, buffer = cv2.imencode('.jpg', detections[0].plot())
            frame_as_text = base64.b64encode(buffer).decode('utf-8')
            socketio.emit('frame', frame_as_text)
            return "Done"
        elif file_extension == 'mp4': 
            video_path = filepath  # replace with your video path
            cap = cv2.VideoCapture(video_path)

            # get video dimensions
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        
            # Define the codec and create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (frame_width, frame_height))
            while cap.isOpened():
                if stop:
                    stop = False
                    break
                ret, frame = cap.read()
                if not ret:
                    break                                                      

                # do YOLOv9 detection on the frame here
                #model = YOLO('yolov9c.pt')
                im0 = frame
                tracks = model.track(im0, persist=True)
                im0 = counter.start_counting(im0, tracks)
                socketio.emit('update_in', counter.in_counts)
                socketio.emit('update_out', counter.out_counts)
                # im0 = speed_obj.estimate_speed(im0, tracks)
                # print(results)
                count_classes = counter.class_wise_count
    

                if (count_classes.__contains__('bus')):
                    socketio.emit('update_bus', count_classes['bus'])
                if (count_classes.__contains__('car')):
                    socketio.emit('update_car', count_classes['car'])
                if (count_classes.__contains__('truck')):
                    socketio.emit('update_truck', count_classes['truck'])

                _, buffer = cv2.imencode('.jpg', im0)
                frame_as_text = base64.b64encode(buffer).decode('utf-8')
                socketio.emit('frame', frame_as_text)
                cv2.waitKey(1)
            return "Done"         

        
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('connected', {'data': 'Connected'})



if __name__ == "__main__":
    # print(torch.cuda.is_available())
    parser = argparse.ArgumentParser(description="Flask app exposing yolov9 models")
    parser.add_argument("--port", default=5000, type=int, help="port number")
    args = parser.parse_args()
    model = YOLO('last.pt')
    model.to(device)
    # Init Object Counter
    region_points = [(20, 400), (1280, 404), (1280, 360), (20, 360)]
    counter = object_counter.ObjectCounter()
    counter.set_args(view_img=False,
                    reg_pts=region_points,
                    classes_names=model.names,
                    draw_tracks=True,
                    line_thickness=2, view_in_counts=False, view_out_counts=False)
    stop = False
    socketio.run(app)
