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

from base64 import b64decode, b64encode
import PIL
import io
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
def connect(data):
    print("cliente connnected")

@socketio.on("clientMessage")
def handle_message_client(data):
    print("message server",data)
    emit("serverResponse","message from server")

@app.route("/send_data",methods=["POST"])
def send_data_postman():
    socketio.emit("serverResponse","message from server")
    return {"message":"success"}



def bbox_to_bytes(bbox_array):
    # convert array into PIL image
    bbox_PIL = PIL.Image.fromarray(bbox_array, 'RGBA')
    iobuf = io.BytesIO()
    # format bbox into png for return
    bbox_PIL.save(iobuf, format='png')
    # format return string
    bbox_bytes = 'data:image/png;base64,{}'.format((str(b64encode(iobuf.getvalue()), 'utf-8')))

    return bbox_bytes


# funcion de cv dnn
# bloque de cv2 dnn
CONFIDENCE_THRESHOLD = 0.6
NMS_THRESHOLD = 0.5
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
class_names=[]
with open("C:/Users/dash/backend/parameters/data.names", 'r') as archivo:
    lineas = archivo.read().splitlines()
    for item in lineas:
      class_names.append(item)

weightsPath_vehicles = "C:/Users/dash/backend/parameters/yolov4-custom_last.weights"# os.path.sep.join(["C://Users//dash//backend//parameter//yolov4-custom_last.weights"])
configPath =  "C:/Users/dash/backend/parameters/yolov4-custom.cfg" # os.path.sep.join(["C://Users//dash//backend//parameter//yolov4-custom.cfg"])
net = cv2.dnn.readNet(configPath, weightsPath_vehicles)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)

# ESTA EJECUCION ES COOM UN WHILE TRUE RECORDAR
#@socketio.on('stream-frame')
#def handle_stream_frame(frame_data):

@app.route("/test_image",methods=["POST"])
def handle_stream_frame():
    # image_data = frame_data.split(",")[1]
    print("location",weightsPath_vehicles)
    # binary_data = base64.b64decode(image_data) # xcd\xfdk\
    COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
    try:
        # PASO 2 : CONVERTIR A DATOS BINARIOS A UNA MATRIZ EN NUMPY
        #opcion 1:
        color = COLORS[0]
        # image_array = np.frombuffer(binary_data, dtype=np.uint8) # [117,]x
        #opcion 2:
        # image_array = np.array(bytearray(binary_data),dtype=np.uint8)
        # PASO 3 : DECODIFICAR LA MATRIZ NUMPY COMO UNA IMAGEN USANDO OPENCV
        # frame = cv2.imdecode(image_array,cv2.IMREAD_COLOR) # matrizes multidimensionales de 0 255
        #cv2.imwrite("test2.png",frame)
            # /mnt/c/Users/dash/backend/predictions_anotations/1697601294.2902837.png
        bbox_array = np.zeros([480,640,4], dtype=np.uint8) # paso 1 crear una matriz en color negro
        #bbox_array = cv2.rectangle(bbox_array, (50, 100), (350, 200),color , 2)
        # **************** funcion de deteccion 
        image = cv2.imread("C:/Users/dash/backend/signa_prueba.jpg")

        classes, scores, boxes = model.detect(image, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
        print("detecto")
        label=""
        for (classid, score, box) in zip(classes, scores, boxes):
            color = COLORS[int(classid) % len(COLORS)]
            # label = "%s : %f" % (class_names[classid], score)
            label = "%s" % (class_names[classid])
            left, top, right, bottom = box
            # cv2.rectangle(frame, box, color, 2)
            # left, top, right, bottom = int(left * width_ratio), int(top * height_ratio), int(right * width_ratio), int(bottom * height_ratio)
            bbox_array = cv2.rectangle(bbox_array,box,color, 2)
            bbox_array = cv2.putText(bbox_array, "{} [{:.2f}]".format(label, float(score)),
                                (left, top - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                color, 2)
        # ****************** terminar la funcion de deteccion                        
        bbox_array[:, :, 3] = (bbox_array.max(axis=2) > 0).astype(int) * 255
        result = image.copy()
        result[bbox_array[:, :, 3] > 0] = bbox_array[:, :, :3][bbox_array[:, :, 3] > 0]
        bbox_bytes = bbox_to_bytes(bbox_array) # converitr a base 64 solo la imagen del cuadro delimitador y el fondo blanco o negro
        print(bbox_bytes) 
        cv2.imwrite("final.png",result)

        emit("serverResponse",bbox_bytes)

        return {"message":"success"}
    except Exception as e:
        print(f"error {str(e)}")
        return {"message":"success"}
    print("frame_data",frame_data)




if __name__ == "__main__":
    socketio.run(app, debug=True,port=5001)
    # app.run(host="127.0.0.1",port=5000,debug=True)
    #  Para ejecutar la aplicación flask con la biblioteca socket.io, necesitamos ejecutar 
    # la instancia de socketio usando socketio.run(), en lugar del habitual app.run(