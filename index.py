from flask import Flask,request
import numpy as np
from flask_cors import CORS
import cv2
import base64
import HandleTracking as ht
from flask_socketio import SocketIO,emit
import sys
import os
import time
# import Detection as detected
app = Flask(__name__)



cors = CORS(app,resources={r"/detection":{"origins":"*"}})
socketio = SocketIO(app,cors_allowed_origins="*")

app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/test")
def test_message():
    return {"message":"test message"}

def check_image(imageSend):
    detector = ht.handDetector(detectionCon=0.75)
    img = detector.findHands(imageSend)
    lmList = detector.findPosition(img)
    description = detector.counting_fingers(lmList)
    descriptionGeneral = f"Se esta mostrando lo siguiente {description}"
    response = {"data": descriptionGeneral }
    imgSave = f"images/{time.time()}.png"
    cv2.imwrite(imgSave,img)
    socketio.emit("message",{"data":description})
    return {"message":description}
###
@app.route("/postman",methods=["POST"])
def customer_postman():
    socketio.emit("message",{"data":"hola desde postman"})
    return {"message":"success"}

@socketio.on("connect")
def connected():
    emit("me",request.sid)


@socketio.on('start-stream')
def handle_stream_frame():
    print("stream started")
    

# ESTA EJECUCION ES COOM UN WHILE TRUE RECORDAR
@socketio.on('stream-frame')
def handle_stream_frame(frame_data):
    image_data = frame_data.split(",")[1]
    binary_data = base64.b64decode(image_data) # xcd\xfdk\
    try:
        # PASO 2 : CONVERTIR A DATOS BINARIOS A UNA MATRIZ EN NUMPY
        #opcion 1:
        image_array = np.frombuffer(binary_data, dtype=np.uint8) # [117,]x
        #opcion 2:
        # image_array = np.array(bytearray(binary_data),dtype=np.uint8)
        # PASO 3 : DECODIFICAR LA MATRIZ NUMPY COMO UNA IMAGEN USANDO OPENCV
        frame = cv2.imdecode(image_array,cv2.IMREAD_COLOR) # matrizes multidimensionales de 0 255
        if img is not None:
            # /mnt/c/Users/dash/backend/predictions_anotations/1697601294.2902837.png
            bbox_array = np.zeros([480,640,4], dtype=np.uint8) # paso 1 crear una matriz en color negro
            # aqui va lo del archivo gpu_cloud
            # paso 8 . devolver la imagen en base 64
            #socketio.emit("image",{"data":bbox})
            print("goo")
        else:
            print("failed to decode the image")
        return {"message":"success"}
    except Exception as e:
        print(f"error {str(e)}")
        return {"message":"success"}
    print("frame_data",frame_data)



@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the server"""
    print("user disconnected")
    # emit("disconnect",f"user {request.sid} disconnected",broadcast=True)
## 


@app.route("/detection",methods=["POST"])
def process_image():
    # detector = htm.handDetector(detectionCon=0.75) # validar aca
    file = request.files["file"]
    # data:image/jpeg;base64,/9j/4AAQSkZJ 
    file_content = file.read()
    image_array = np.frombuffer(file_content, dtype=np.uint8) # [117,]x
    frame = cv2.imdecode(image_array,cv2.IMREAD_COLOR) # matrizes multidimensionales de 0 255
    cv2.imwrite("file.jpg",frame)
    cmd = f'wsl.exe python3 /mnt/c/Users/Maria/Desktop/tesisjota/ProyectoWeb/detection.py --image {nameFile}'
    # requerido ignorar data:image/jpeg;base64
    return {"message":"success"}


if __name__ == "__main__":
    socketio.run(app, debug=True,port=5001)
    # app.run(host="127.0.0.1",port=5000,debug=True)
    #  Para ejecutar la aplicación flask con la biblioteca socket.io, necesitamos ejecutar 
    # la instancia de socketio usando socketio.run(), en lugar del habitual app.run(