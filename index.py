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
from Detection import DetectedImage
from base64 import b64decode, b64encode
import PIL
from datetime import datetime
import io
# import Detection as detected
app = Flask(__name__)

TOTAL_PUNTOS=3

cors = CORS(app,resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app,cors_allowed_origins="*")

app.config['CORS_HEADERS'] = 'Content-Type'


data_check=[] # ARRAY DE LETRAS CORRECTAS
data_test = [] # array de datos a buscar tomar siempre el ultimo a buscar
draw_image_array=[] # array de dibujo de imagenes
tiempo_detectado_letra = [] # array de tiempo detectado por letra
tiempo_inicio_array=[] # array de fecha de inicio restablecer
array_image=[]

detected = DetectedImage() # instanciar la clase
bbox_end,random_file = detected.generate_image(data_test)
tiempo_inicio_array.append(time.time()) # establecer tiempo
draw_image_array.append(bbox_end) # establecer matriz de imagenes nuevas a detectar
# variables de puntos
total_general = 0
data_test.append(random_file) # random_file

name_directory = time.time()
directorySave = os.path.join(os.getcwd(),str(name_directory))

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/api/list_register",methods=["GET"])
def connect(data):
    print("cliente connnected")

@app.route("/api/register",methods=["POST"])
def send_data_man():
    # option postman
    # data = request.get_json()  # Obténer los datos JSON de la solicitud
    # print(data["name"])
    # option web browser
    data = request.get_json()
    nameUser = data.get("name")
    detected.define_user(0,nameUser)

    # uuid_user = f"{time.time()}_{data["name"]}_point"
    # detected.redis_client.set(uuid_user,0)
    return {"total_points":TOTAL_PUNTOS}

# CONFIDENCE_THRESHOLD = 0.6 labels
# NMS_THRESHOLD = 0.5
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
class_names=[]
file_names = os.path.join(os.getcwd(),"parameter","obj.names")
with open(file_names, 'r') as archivo:
    lineas = archivo.read().splitlines()
    for item in lineas:
      class_names.append(item)



# directorySave=f"/content/{name_directory}"
# os.mkdir(directorySave)
# ESTA EJECUCION ES COOM UN WHILE TRUE RECORDAR
@socketio.on('stream-frame')
def handle_stream_frame(frame_data):
# @app.route("/test_image",methods=["POST"])
# def handle_stream_frame():
    global data_test
    global data_check
    global draw_image_array
    image_data = frame_data.split(",")[1]
    binary_data = base64.b64decode(image_data) # xcd\xfdk\
    # point = 0

    COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
    try:
        # PASO 2 : CONVERTIR A DATOS BINARIOS A UNA MATRIZ EN NUMPY
        #opcion 1:
        color = COLORS[0]
        image_array = np.frombuffer(binary_data, dtype=np.uint8) # [117,]x
        #opcion 2:
        # image_array = np.array(bytearray(binary_data),dtype=np.uint8)
        # PASO 3 : DECODIFICAR LA MATRIZ NUMPY COMO UNA IMAGEN USANDO OPENCV
        frame = cv2.imdecode(image_array,cv2.IMREAD_COLOR) # matrizes multidimensionales de 0 255
        #cv2.imwrite("test2.png",frame)
            # /mnt/c/Users/dash/backend/predictions_anotations/1697601294.2902837.png
        bbox_array = np.zeros([480,640,4], dtype=np.uint8) # paso 1 crear una matriz en color negro
        tiempo_transcurido = time.time() - tiempo_inicio_array[-1]

        #bbox_array = cv2.rectangle(bbox_array, (50, 100), (350, 200),color , 2)
        # **************** funcion de deteccion 
        # image = cv2.imread("/Users/dash/Desktop/signas_project/detectado.png")
        print(f"inicio deteccion {datetime.now().time()}")
        classes, scores, boxes = detected.detection(frame)
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
        result = frame.copy()
        print("detecto" , label)
        print(f"final deteccion {datetime.now().time()}")
        result[bbox_array[:, :, 3] > 0] = bbox_array[:, :, :3][bbox_array[:, :, 3] > 0]
        bbox_bytes = detected.bbox_to_bytes(bbox_array) # converitr a base 64 solo la imagen del cuadro delimitador y el fondo blanco o negro
        # ***** validar label
        print("label " , label," label detectado " ,data_test[-1])
        print("username",detected.username)
        if label == data_test[-1]:
            detected.point += 1
            print("detecto correctamente")
            bbox_end,random_file = detected.generate_image(data_test)
            data_test.append(random_file) # palabra nueva
            draw_image_array.append(bbox_end) # imagen nueva
            data_check.append(label) # palabra acertada (DATAFRAME USED)
            # tiempo
            # minutos,segundos = detected.convert_segundos_a_minutos(int(tiempo_transcurido))
            # total_general += tiempo_transcurido
            # texto_tiempo =  f"se detecto {minutos} minuto en {segundos} segundos la letra {label}"
            # tiempo_detectado_letra.append(texto_tiempo) # (DATAFRAME USED)
            # fin de nuevo
            saveFile = f"{directorySave}/{label}.png"
            #array_image.append(saveFile) # array de imagenes detectadas (DATAFRAME USED)
            # cv2.imwrite(saveFile,result)
            #tiempo_inicio_array.append(time.time()) # establecer tiempo
        
        socketio.emit("serverResponse",{"bbox":bbox_bytes,"pointTotal":TOTAL_PUNTOS,"image":draw_image_array[-1],"point":detected.point})
        print("TOTAL_PUNTOS",TOTAL_PUNTOS)
        print("TOTAL GANADO",detected.point)
    except Exception as e:
        print(f"error {str(e)}")
        return {"message":"success"}



if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0',debug=True,port=5001)
    # app.run(host="127.0.0.1",port=5000,debug=True)
    #  Para ejecutar la aplicación flask con la biblioteca socket.io, necesitamos ejecutar 
    # la instancia de socketio usando socketio.run(), en lugar del habitual app.run(