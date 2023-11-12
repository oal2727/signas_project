# import darknet functions to perform object detections
from darknet.darknet import *
from base64 import b64decode, b64encode
import PIL
import io

# load in our YOLOv4 architecture network
class DetectedImage:
  def __init__(self):
    self.network, class_names, class_colors = load_network(
        "/content/gdrive/MyDrive/signas/parameters/yolov4-custom.cfg", 
        "/content/gdrive/MyDrive/signas/parameters/names.data", 
        "/content/gdrive/MyDrive/signas/parameters/yolov4-custom_last_4500.weights"
    )
    self.className = class_names
    self.colors = class_colors
    self.width = network_width(self.network)
    self.height = network_height(self.network)


  def darknet_helper(self,img):
    darknet_image = make_image(self.width, self.height, 3)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (self.width, self.height),
                                interpolation=cv2.INTER_LINEAR)
    # get image ratios to convert bounding boxes to proper size
    img_height, img_width, _ = img.shape
    width_ratio = img_width/self.width
    height_ratio = img_height/self.height

    # run model on darknet style image to get detections
    copy_image_from_bytes(darknet_image, img_resized.tobytes())
    detections = detect_image(self.network, self.className, darknet_image)
    free_image(darknet_image)
    return detections, width_ratio, height_ratio
  def generate_image(self,data_test):
    directory_path = "/content/gdrive/MyDrive/signas/imagenes"
    all_files = os.listdir(directory_path)
    while True:
      random_file = random.choice(all_files)
      nameSplit= random_file.split(".")[0] # obtener solo la letra
      nameFileImage=f"/content/gdrive/MyDrive/signas/imagenes/{random_file}"
      if nameSplit not in data_test: # no volver a repetir si ya fue detectado
        with open(nameFileImage, 'rb') as image_file:
          bbox_bytes = base64.b64encode(image_file.read()).decode("utf-8")
          bbox_end = f"data:image/jpg;base64,{bbox_bytes}"
          return bbox_end,nameSplit

  def loop_detection(self,detections,bbox,width_ratio,height_ratio,bbox_array):
    for label, confidence, bbox in detections:
      left, top, right, bottom = bbox2points(bbox)
      left, top, right, bottom = int(left * width_ratio), int(top * height_ratio), int(right * width_ratio), int(bottom * height_ratio)
      bbox_array = cv2.rectangle(bbox_array, (left, top), (right, bottom), class_colors[label], 2)
      bbox_array = cv2.putText(bbox_array, "{} [{:.2f}]".format(label, float(confidence)),
                        (left, top - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        class_colors[label], 2)
      return bbox_array
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
