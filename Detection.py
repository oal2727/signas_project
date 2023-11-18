# import darknet functions to perform object detections
# from darknet.darknet import *
from base64 import b64decode, b64encode
import PIL
import io
import os
import random
import base64
import cv2
import time
import redis
# load in our YOLOv4 architecture network
class DetectedImage():
  def __init__(self):
    self.CONFIDENCE_THRESHOLD = 0.6
    self.NMS_THRESHOLD = 0.5
    self.point=0
    self.username=""
    self.COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
    weightsPath_vehicles = "/Users/dash/Desktop/signas_project/parameter/yolov4-custom_last_4500.weights"# os.path.sep.join(["C://Users//dash//backend//parameter//yolov4-custom_last.weights"])
    configPath =  "/Users/dash/Desktop/signas_project/parameter/yolov4-custom.cfg" # os.path.sep.join(["C://Users//dash//backend//parameter//yolov4-custom.cfg"])
    net = cv2.dnn.readNet(configPath, weightsPath_vehicles)
    # net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    # net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU  )
    self.model = cv2.dnn_DetectionModel(net)
    self.model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)
  def define_user(self,point,username):
    self.point = point
    self.username = f"{time.time()}_{username}"
  def labels(self):
    class_names=[]
    with open("/Users/dash/Desktop/signas_project/parameter/obj.names", 'r') as archivo:
        lineas = archivo.read().splitlines()
        for item in lineas:
          class_names.append(item)
    return class_names

  def detection(self,frame):
    classes, scores, boxes = self.model.detect(
    frame, 
    self.CONFIDENCE_THRESHOLD, 
    self.NMS_THRESHOLD)
    return classes,scores,boxes
  def generate_image(self,data_test):
    nameDirectoryImages = "imagenes"
    directory_path = os.path.join(os.getcwd(),nameDirectoryImages)
    all_files = os.listdir(directory_path)
    while True:
      random_file = random.choice(all_files)
      nameSplit= random_file.split(".")[0] # obtener solo la letra
      nameFileImage = os.path.join(os.getcwd(),nameDirectoryImages,random_file)
      # nameFileImage=f"/content/gdrive/MyDrive/signas/imagenes/{random_file}"
      if nameSplit not in data_test: # no volver a repetir si ya fue detectado
        with open(nameFileImage, 'rb') as image_file:
          bbox_bytes = base64.b64encode(image_file.read()).decode("utf-8")
          bbox_end = f"data:image/jpg;base64,{bbox_bytes}"
          return bbox_end,nameSplit

  def convert_segundos_a_minutos(self,segundos):
    minutos = segundos // 60
    segundos_restantes = segundos % 60
    return minutos,segundos_restantes
  # directory(repository),bbox(array_data),label(text),data_test(text_detection),bbbox_array(imagen new),data_check(text well) 
  # | tiempo_detectado_letra(data_frame_text),array_image(data_Frame),tiempo_inicio_array(tiempo_array)
  def validate_label(self,label,total_general,directorySave,bbox,data_test,bbbox_array,data_check,tiempo_detectado_letra,array_image,tiempo_inicio_array):
    if label == data_test[-1]:
      bbox_end,random_file = self.generate_image(data_test)
      data_test.append(random_file) # palabra nueva
      bbbox_array.append(bbox_end) # imagen nueva
      data_check.append(label) # palabra acertada (DATAFRAME USED)
      # tiempo
      minutos,segundos = self.convert_segundos_a_minutos(int(tiempo_transcurido))
      total_general += tiempo_transcurido
      texto_tiempo =  f"se detecto {minutos} minuto en {segundos} segundos la letra {label}"
      tiempo_detectado_letra.append(texto_tiempo) # (DATAFRAME USED)
      # saveFile = f"{directorySave}/{label}.png"
      saveFile = self.save_file(directorySave,label,bbox)
      array_image.append(saveFile) # array de imagenes detectadas (DATAFRAME USED)
      tiempo_inicio_array.append(time.time()) # establecer tiempo
      # crear data frame del valor encontrado
    return data_test,bbbox_array,data_check,tiempo_detectado_letra,array_image,tiempo_inicio_array
      # ----
  def save_file(self,directorySave,label,bbox):
    saveFile = f"{directorySave}/{label}.png"
    cv2.imwrite(saveFile,bbox)
    return saveFile

  def generar_dataframe(self,array_image,data_check,tiempo_detectado_letra):
    resultados_df = pd.DataFrame(columns=["archivo", "texto_detectado","tiempo"])

    array_datos={
      "archivo":array_image, # array_image  [1,2,3,4]
      "texto_detectado":data_check, # data_check
      "tiempo":tiempo_detectado_letra # tiempo_detectado_letra
    }
    data_Frame_data = pd.DataFrame(array_datos)

    resultados_df = pd.concat([resultados_df, data_Frame_data], ignore_index=True)

    resultados_df.to_excel(f'{directorySave}/detectado.xlsx', index=False)


  def js_to_image(self,js_reply):
    # decode base64 image
    image_bytes = b64decode(js_reply.split(',')[1])
    # convert bytes to numpy array
    jpg_as_np = np.frombuffer(image_bytes, dtype=np.uint8)
    # decode numpy array into OpenCV BGR image
    img = cv2.imdecode(jpg_as_np, flags=1)

    return img
  # función para convertir la imagen del cuadro delimitador del rectángulo OpenCV en una cadena de bytes base64 para superponerla en la transmisión de video
  def bbox_to_bytes(self,bbox_array):
    # convert array into PIL image
    bbox_PIL = PIL.Image.fromarray(bbox_array, 'RGBA')
    iobuf = io.BytesIO()
    # format bbox into png for return
    bbox_PIL.save(iobuf, format='png')
    # format return string
    bbox_bytes = 'data:image/png;base64,{}'.format((str(b64encode(iobuf.getvalue()), 'utf-8')))

    return bbox_bytes
