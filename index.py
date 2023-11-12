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
import Detection as detected
app = Flask(__name__)



cors = CORS(app,resources={r"/detection":{"origins":"*"}})
socketio = SocketIO(app,cors_allowed_origins="*")

app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

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
            detections, width_ratio, height_ratio = detected.darknet_helper(frame) # paso 2 obtener array de deteccion
            # paso 3 asignar el cuadro delimitador a la matriz negra
            for label, confidence, bbox in detections:
                left, top, right, bottom = bbox2points(bbox)
                left, top, right, bottom = int(left * width_ratio), int(top * height_ratio), int(right * width_ratio), int(bottom * height_ratio)
                bbox_array = cv2.rectangle(bbox_array, (left, top), (right, bottom), detected.colors[label], 2)
                bbox_array = cv2.putText(bbox_array, "{} [{:.2f}]".format(label, float(confidence)),
                                    (left, top - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    detected.colors[label], 2)
            bbox_array[:, :, 3] = (bbox_array.max(axis=2) > 0).astype(int) * 255 # Paso 4 . Este fragmento calcula el valor máximo a lo largo del eje de los canales de color
            result = frame.copy() # paso 5 . crear una copia de la imagen original
            # paso 6 . asigna los valores de los canales RGB de bbox_array (para los píxeles que tienen algún color) a los píxeles correspondientes en la imagen
            result[bbox_array[:, :, 3] > 0] = bbox_array[:, :, :3][bbox_array[:, :, 3] > 0] # 
            #    data_test,draw_image_array,data_check,tiempo_detectado_letra,array_image,tiempo_inicio_array = detected.validate_label(label,total_general,directorySave,result,data_test,draw_image_array,data_check,tiempo_detectado_letra,array_image,tiempo_inicio_array)
            # if len(data_check) == TOTAL_DE_CARACTERES_ACERTAR:
                # print(f"FELICIDADES GANASTE {nombre_persona} ")
                # break
            # paso 7 . convertir la imagen a base64
            bbox = detected.bbox_to_bytes(bbox_array)
            # paso 8 . devolver la imagen en base 64
            socketio.emit("image",{"data":bbox})

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

    # data:image/jpeg;base64,/9j/4AAQSkZJ 
    # comenzar desde /9j/4AAQSkZJ (requerido recortar)
    data = request.json["data"]
    # requerido ignorar data:image/jpeg;base64
    image_data = data.split(",")[1]
    binary_data = base64.b64decode(image_data) # xcd\xfdk\
    try:
        # PASO 2 : CONVERTIR A DATOS BINARIOS A UNA MATRIZ EN NUMPY
        #opcion 1:
        image_array = np.frombuffer(binary_data, dtype=np.uint8) # [117,]
        #opcion 2:
        # image_array = np.array(bytearray(binary_data),dtype=np.uint8)
        # PASO 3 : DECODIFICAR LA MATRIZ NUMPY COMO UNA IMAGEN USANDO OPENCV
        img = cv2.imdecode(image_array,cv2.IMREAD_COLOR) # matrizes multidimensionales de 0 255
        if img is not None:
            cv2.imwrite("image.png",img)
            return check_image(img)
        else:
            print("failed to decode the image")
        return {"message":"success"}
    except Exception as e:
        print(f"error {str(e)}")
        return {"message":"success"}


if __name__ == "__main__":
    socketio.run(app, debug=True,port=5001)
    # app.run(host="127.0.0.1",port=5000,debug=True)
    #  Para ejecutar la aplicación flask con la biblioteca socket.io, necesitamos ejecutar 
    # la instancia de socketio usando socketio.run(), en lugar del habitual app.run(